import os
import requests
from unidiff import PatchSet
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def initialize_model():
    """Initialize code review model with educational prompt"""
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codereviewer")
    model = AutoModelForSeq2SeqLM.from_pretrained("microsoft/codereviewer")
    
    # Set educational prompt prefix
    model.config.prefix = (
        "You are a friendly coding mentor. "
        "Explain concepts like you're teaching a student. "
        "Use simple terms, emojis, and concrete examples. "
        "Format: ✅ Great Job, 💡 Tip, 🚨 Issue"
    )
    return tokenizer, model

def fetch_pr_diff():
    """Get PR diff from GitHub"""
    repo = os.environ['REPO_NAME']
    pr_number = os.environ['PR_NUMBER']
    token = os.environ['GITHUB_TOKEN']
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers=headers
    )
    response.raise_for_status()
    return response.text

def fetch_pr_head_sha():
    """Get latest commit SHA for the PR"""
    repo = os.environ['REPO_NAME']
    pr_number = os.environ['PR_NUMBER']
    token = os.environ['GITHUB_TOKEN']
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(pr_url, headers=headers)
    response.raise_for_status()
    return response.json()['head']['sha']

def generate_review_comment(old_code, new_code):
    """Generate educational code review comments"""
    input_text = (
        f"Old code:\n{old_code}\n===\nNew code:\n{new_code}\n===\n"
        "Please explain changes in a way that helps students learn. "
        "First praise good practices, then suggest improvements. "
        "Use friendly language and simple examples."
    )
    
    inputs = tokenizer(input_text, return_tensors="pt", 
                      truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_length=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def post_review(comments):
    """Post review comments and status checks to GitHub"""
    repo = os.environ['REPO_NAME']
    pr_number = os.environ['PR_NUMBER']
    token = os.environ['GITHUB_TOKEN']
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Post status check
    pr_head_sha = fetch_pr_head_sha()
    check_url = f"https://api.github.com/repos/{repo}/check-runs"
    check_response = requests.post(check_url, headers=headers, json={
        "name": "Code Review Bot",
        "head_sha": pr_head_sha,
        "status": "completed",
        "conclusion": "failure" if comments else "success",
        "output": {
            "title": "Code Review Results",
            "summary": f"Found {len(comments)} suggestions" if comments 
                      else "No issues found!",
            "text": "See individual comments for details"
        }
    })
    
    # Post review comments
    review_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    review_response = requests.post(review_url, headers=headers, json={
        "body": "Learning-focused code review feedback",
        "event": "REQUEST_CHANGES" if comments else "APPROVE",
        "comments": [{
            "path": c["path"],
            "position": c["position"],
            "body": c["body"]
        } for c in comments]
    })
    
    if review_response.status_code not in (200, 201):
        print(f"Review failed: {review_response.text}")
        exit(1)
    elif comments:
        exit(1)  # Fail CI check if there are comments

def main():
    # Initialize model and tokenizer
    global tokenizer, model
    tokenizer, model = initialize_model()
    
    # Process PR diff
    diff_text = fetch_pr_diff()
    patch_set = PatchSet(diff_text)
    comments = []
    
    for patched_file in patch_set:
        if patched_file.is_removed_file:
            continue
            
        for hunk in patched_file:
            for idx, line in enumerate(hunk):
                if line.is_added:
                    try:
                        # Get context lines
                        context = [hunk[i] for i in range(
                            max(0, idx-3), 
                            min(len(hunk), idx+4)
                        )]
                        
                        old_code = []
                        new_code = []
                        for ctx_line in context:
                            if ctx_line.is_removed:
                                old_code.append(ctx_line.value.rstrip('\n'))
                            elif ctx_line.is_added:
                                new_code.append(ctx_line.value.rstrip('\n'))
                            else:
                                old_code.append(ctx_line.value.rstrip('\n'))
                                new_code.append(ctx_line.value.rstrip('\n'))
                        
                        if old_code and new_code:
                            comment = generate_review_comment(
                                '\n'.join(old_code),
                                '\n'.join(new_code)
                            )
                            if comment.strip():
                                comments.append({
                                    "path": patched_file.path,
                                    "position": idx + 1,  # GitHub uses 1-based index
                                    "body": comment
                                })
                    except Exception as e:
                        print(f"Error processing line: {str(e)}")
                        continue
    
    # Post results to GitHub
    if comments:
        post_review(comments)
    else:
        print("No review comments generated")

if __name__ == "__main__":
    main()