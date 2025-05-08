import os
import json
import pandas as pd
import openai
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import AnalysisPrompt, AnalysisRun
from .forms import UploadBatchForm, AnalysisPromptForm, AnalyzeBatchForm
from .serializers import AnalysisPromptSerializer, AnalysisRunSerializer
from dashboard.models import FeedbackBatch, FeedbackItem, FeedbackCategory, FeedbackSource

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

@login_required
def prompt_list(request):
    """View to list all analysis prompts"""
    prompts = AnalysisPrompt.objects.filter(client=request.user)
    
    if request.method == 'POST':
        form = AnalysisPromptForm(request.POST)
        if form.is_valid():
            prompt = form.save(commit=False)
            prompt.client = request.user
            prompt.save()
            messages.success(request, 'Prompt created successfully!')
            return redirect('analysis:prompt_list')
    else:
        form = AnalysisPromptForm()
    
    return render(request, 'analysis/prompt_list.html', {
        'prompts': prompts,
        'form': form
    })

@login_required
def prompt_detail(request, pk):
    """View to show and edit a specific prompt"""
    prompt = get_object_or_404(AnalysisPrompt, pk=pk, client=request.user)
    
    if request.method == 'POST':
        form = AnalysisPromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prompt updated successfully!')
            return redirect('analysis:prompt_detail', pk=pk)
    else:
        form = AnalysisPromptForm(instance=prompt)
    
    return render(request, 'analysis/prompt_detail.html', {
        'prompt': prompt,
        'form': form
    })

@login_required
def run_list(request):
    """View to list all analysis runs"""
    runs = AnalysisRun.objects.filter(client=request.user).order_by('-started_at')
    
    # Count runs by status for statistics
    completed_count = runs.filter(status='completed').count()
    in_progress_count = runs.filter(status='in_progress').count()
    failed_count = runs.filter(status='failed').count()
    
    return render(request, 'analysis/run_list.html', {
        'runs': runs,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'failed_count': failed_count
    })

@login_required
def run_detail(request, pk):
    """View to show details of a specific analysis run"""
    run = get_object_or_404(AnalysisRun, pk=pk, client=request.user)
    feedback_items = FeedbackItem.objects.filter(
        client=request.user, 
        batch=run.batch
    ).order_by('-created_at')
    
    return render(request, 'analysis/run_detail.html', {
        'run': run,
        'feedback_items': feedback_items
    })

@login_required
def upload_batch(request):
    """View to upload a new batch of feedback"""
    if request.method == 'POST':
        form = UploadBatchForm(request.POST, request.FILES)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.client = request.user
            batch.save()
            
            # Process the uploaded file
            file_path = batch.original_file.path
            try:
                df = pd.read_csv(file_path)
                
                # Basic validation of the CSV structure
                required_columns = ['content', 'rating']
                for col in required_columns:
                    if col not in df.columns:
                        messages.error(request, f"Missing required column: {col}")
                        batch.delete()  # Delete the batch if validation fails
                        return redirect('analysis:upload_batch')
                
                # Store the number of rows for later processing
                batch.total_items = len(df)
                batch.save()
                
                messages.success(request, f'Batch "{batch.name}" uploaded successfully with {batch.total_items} items!')
                return redirect('analysis:analyze_batch', batch_id=batch.id)
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                batch.delete()  # Delete the batch if processing fails
                return redirect('analysis:upload_batch')
    else:
        form = UploadBatchForm()
    
    return render(request, 'analysis/upload_batch.html', {'form': form})

@login_required
def analyze_batch(request, batch_id):
    """View to analyze a batch of feedback"""
    batch = get_object_or_404(FeedbackBatch, pk=batch_id, client=request.user)
    
    if request.method == 'POST':
        form = AnalyzeBatchForm(request.POST, client=request.user)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            
            # Create a new analysis run
            run = AnalysisRun.objects.create(
                batch=batch,
                prompt=prompt,
                client=request.user,
                status='in_progress',
                total_items=batch.total_items
            )
            
            # Start the analysis process (in a real app, this would be a background task)
            try:
                process_batch(run)
                return redirect('analysis:run_detail', pk=run.id)
            except Exception as e:
                run.status = 'failed'
                run.error_message = str(e)
                run.save()
                messages.error(request, f"Error analyzing batch: {str(e)}")
                return redirect('analysis:analyze_batch', batch_id=batch_id)
    else:
        form = AnalyzeBatchForm(client=request.user)
    
    return render(request, 'analysis/analyze_batch.html', {
        'batch': batch,
        'form': form
    })

@login_required
def download_results(request, run_id):
    """View to download analysis results as CSV"""
    run = get_object_or_404(AnalysisRun, pk=run_id, client=request.user)
    
    # Get all feedback items for this run
    feedback_items = FeedbackItem.objects.filter(
        client=request.user,
        batch=run.batch
    )
    
    # Create a DataFrame from the feedback items
    data = []
    for item in feedback_items:
        data.append({
            'id': item.id,
            'content': item.content,
            'category': item.category.name if item.category else 'Uncategorized',
            'rating': item.rating,
            'sentiment_score': item.sentiment_score,
            'source': item.source.name,
            'processed': item.processed,
            'feedback_date': item.feedback_date
        })
    
    df = pd.DataFrame(data)
    
    # Create the response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{run.batch.name}_results.csv"'
    
    # Write the CSV to the response
    df.to_csv(response, index=False)
    
    return response

# Helper function to process a batch of feedback
def process_batch(run):
    """Process a batch of feedback using OpenAI API"""
    batch = run.batch
    prompt_template = run.prompt.prompt_template
    
    # Read the CSV file
    file_path = batch.original_file.path
    df = pd.read_csv(file_path)
    
    # Get or create categories
    positive_category, _ = FeedbackCategory.objects.get_or_create(name='Positive')
    negative_category, _ = FeedbackCategory.objects.get_or_create(name='Negative')
    neutral_category, _ = FeedbackCategory.objects.get_or_create(name='Neutral')
    feature_request, _ = FeedbackCategory.objects.get_or_create(name='Feature Request')
    bug_report, _ = FeedbackCategory.objects.get_or_create(name='Bug Report')
    
    # Process each row
    processed_count = 0
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    
    for _, row in df.iterrows():
        content = row['content']
        rating = row.get('rating', None)
        customer_id = row.get('customer_id', None)
        feedback_date = row.get('feedback_date', None)
        
        # Format the prompt with the feedback content
        formatted_prompt = prompt_template.format(feedback=content)
        
        try:
            # Call the OpenAI API with the new client-based approach
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a feedback analyzer. Categorize the feedback into one of these categories: Positive, Negative, Neutral, Feature Request, or Bug Report. Also, provide a sentiment score from -1 (very negative) to 1 (very positive)."},
                    {"role": "user", "content": formatted_prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            # Extract the result
            result = response.choices[0].message.content
            
            # Parse the result (assuming a standardized format)
            # In a real app, this parsing would be more robust
            category_name = None
            sentiment_score = None
            
            if "positive" in result.lower():
                category_name = 'Positive'
            elif "negative" in result.lower():
                category_name = 'Negative'
            elif "neutral" in result.lower():
                category_name = 'Neutral'
            elif "feature request" in result.lower():
                category_name = 'Feature Request'
            elif "bug report" in result.lower():
                category_name = 'Bug Report'
            
            # Try to extract sentiment score
            import re
            score_match = re.search(r'sentiment score:?\s*([-+]?\d*\.\d+|\d+)', result.lower())
            if score_match:
                sentiment_score = float(score_match.group(1))
            
            # Determine the category object
            category = None
            if category_name == 'Positive':
                category = positive_category
            elif category_name == 'Negative':
                category = negative_category
            elif category_name == 'Neutral':
                category = neutral_category
            elif category_name == 'Feature Request':
                category = feature_request
            elif category_name == 'Bug Report':
                category = bug_report
            
            # Create the feedback item
            FeedbackItem.objects.create(
                client=run.client,
                batch=batch,  # Important: Associate with the batch!
                source=batch.source,
                category=category,
                content=content,
                rating=rating,
                sentiment_score=sentiment_score,
                processed=True,
                customer_id=customer_id,
                feedback_date=feedback_date
            )
            
            # Update progress
            processed_count += 1
            run.processed_items = processed_count
            run.save()
            
        except Exception as e:
            # Log the error but continue processing
            print(f"Error processing item: {str(e)}")
    
    # Update the run status
    run.status = 'completed'
    run.completed_at = timezone.now()
    run.save()
    
    # Update the batch status
    batch.processed = True
    batch.save()

# API Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_prompt_list(request):
    """API endpoint to list and create analysis prompts"""
    if request.method == 'GET':
        prompts = AnalysisPrompt.objects.filter(client=request.user)
        serializer = AnalysisPromptSerializer(prompts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AnalysisPromptSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(client=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_prompt_detail(request, pk):
    """API endpoint to get, update or delete a specific prompt"""
    try:
        prompt = AnalysisPrompt.objects.get(pk=pk, client=request.user)
    except AnalysisPrompt.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AnalysisPromptSerializer(prompt)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = AnalysisPromptSerializer(prompt, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        prompt.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_run_list(request):
    """API endpoint to list analysis runs"""
    runs = AnalysisRun.objects.filter(client=request.user).order_by('-started_at')
    serializer = AnalysisRunSerializer(runs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_run_detail(request, pk):
    """API endpoint to get a specific analysis run"""
    try:
        run = AnalysisRun.objects.get(pk=pk, client=request.user)
    except AnalysisRun.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = AnalysisRunSerializer(run)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upload_batch(request):
    """API endpoint to upload a new batch of feedback"""
    # Extract form data
    name = request.data.get('name')
    source_id = request.data.get('source')
    file = request.FILES.get('file')
    
    if not all([name, source_id, file]):
        return Response(
            {'error': 'Missing required fields (name, source, file)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        source = FeedbackSource.objects.get(pk=source_id)
    except FeedbackSource.DoesNotExist:
        return Response(
            {'error': 'Invalid source ID'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create the batch
    batch = FeedbackBatch.objects.create(
        name=name,
        source=source,
        client=request.user,
        original_file=file
    )
    
    # Process the file
    try:
        df = pd.read_csv(batch.original_file.path)
        
        # Basic validation
        required_columns = ['content', 'rating']
        for col in required_columns:
            if col not in df.columns:
                batch.delete()
                return Response(
                    {'error': f'Missing required column: {col}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        batch.total_items = len(df)
        batch.save()
        
        from dashboard.serializers import FeedbackBatchSerializer
        serializer = FeedbackBatchSerializer(batch)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        batch.delete()
        return Response(
            {'error': f'Error processing file: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_analyze_batch(request, batch_id):
    """API endpoint to analyze a batch of feedback"""
    try:
        batch = FeedbackBatch.objects.get(pk=batch_id, client=request.user)
    except FeedbackBatch.DoesNotExist:
        return Response(
            {'error': 'Batch not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    prompt_id = request.data.get('prompt_id')
    if not prompt_id:
        return Response(
            {'error': 'Missing prompt_id'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        prompt = AnalysisPrompt.objects.get(pk=prompt_id, client=request.user)
    except AnalysisPrompt.DoesNotExist:
        return Response(
            {'error': 'Invalid prompt ID'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create a new analysis run
    run = AnalysisRun.objects.create(
        batch=batch,
        prompt=prompt,
        client=request.user,
        status='in_progress',
        total_items=batch.total_items
    )
    
    # In a real app, you'd start the analysis in a background task
    # Here we'll just respond immediately with the run info
    serializer = AnalysisRunSerializer(run)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_run_status(request, pk):
    """API endpoint to get the status of a run"""
    try:
        run = AnalysisRun.objects.get(pk=pk, client=request.user)
    except AnalysisRun.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    data = {
        'id': run.id,
        'status': run.status,
        'progress': run.progress_percentage,
        'total_items': run.total_items,
        'processed_items': run.processed_items,
        'error_message': run.error_message
    }
    
    return Response(data)