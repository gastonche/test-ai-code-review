import os
import requests
from unidiff import PatchSet
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

def initialize_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained("microsoft/codereviewer")
        model = AutoModelForSeq2SeqLM.from_pretrained("microsoft/codereviewer")
        return tokenizer, model
    except Exception as e:
        print(f"Model initialization failed: {str(e)}")
        exit(1)

def fetch_pr_diff():
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

def generate_review_comment(old_code, new_code):
    input_text = f"Old code:\n{old_code}\nNew code:\n{new_code}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_length=128)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def post_comment_to_pr(reviews):
    repo = os.environ['REPO_NAME']
    pr_number = os.environ['PR_NUMBER']
    token = os.environ['GITHUB_TOKEN']
    
    comments = []
    for file_path, line_number, comment_body in reviews:
        # Truncate comment if too long
        if len(comment_body) > 65536:
            comment_body = comment_body[:65000] + "\n\n[COMMENT TRUNCATED]"
        comments.append({
            "path": file_path,
            "line": line_number,  # Changed from 'position' to 'line'
            "body": f"**CodeReviewer Suggestion:**\n{comment_body}"
        })
    
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": "AI Code Review Comments",
        "event": "COMMENT",
        "comments": comments
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error posting comment: {str(e)}")
        print(f"Response: {response.text}")

def main():
    diff_text = fetch_pr_diff()
    patch_set = PatchSet(diff_text)
    
    comments = []
    
    for patched_file in patch_set:
        if patched_file.is_removed_file:
            continue
        
        for hunk in patched_file:
            for line in hunk:
                if line.is_added:
                    try:
                        # Safely get line numbers with None checks
                        line_no = line.target_line_no
                        if line_no is None:
                            continue
                            
                        old_code = []
                        new_code = []
                        # Get surrounding context
                        context_lines = 3
                        start_line = max(1, line_no - context_lines)
                        
                        for ctx_line in hunk:
                            if ctx_line.target_line_no is None:
                                continue
                            if abs(ctx_line.target_line_no - line_no) <= context_lines:
                                if ctx_line.is_removed:
                                    old_code.append(ctx_line.value.rstrip('\n'))
                                elif ctx_line.is_added:
                                    new_code.append(ctx_line.value.rstrip('\n'))
                                else:
                                    old_code.append(ctx_line.value.rstrip('\n'))
                                    new_code.append(ctx_line.value.rstrip('\n'))
                        
                        if old_code and new_code:
                            review_comment = generate_review_comment('\n'.join(old_code), '\n'.join(new_code))
                            if review_comment.strip():
                                comments.append({
                                    "path": patched_file.path,
                                    "line": line_no,
                                    "body": review_comment
                                })
                    except Exception as e:
                        print(f"Error processing line: {str(e)}")
                        continue
    
    if comments:
        try:
            # Post comments in batches of 10 to avoid API limits
            reviews = []
            for i in range(0, len(comments), 10):
                batch = comments[i:i+10]
                reviews.append((batch[0]["path"], batch[0]["line"], 
                                 "\n\n---\n\n".join([c["body"] for c in batch])))
            if len(reviews) > 0:
                post_comment_to_pr(reviews)
        except Exception as e:
            print(f"Error posting comments: {str(e)}")

if __name__ == "__main__":
    tokenizer, model = initialize_model()
    main()