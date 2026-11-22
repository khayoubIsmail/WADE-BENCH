import json

def parse_and_save():
    try:
        with open(r'C:\Users\HP\.gemini\antigravity-ide\brain\ab493cf0-ff26-4c69-9099-58993592f9e2\.system_generated\steps\20203\output.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '### Result\n' in content:
            result_part = content.split('### Result\n')[1].split('### Ran Playwright code')[0].strip()
            
            if result_part.startswith('"') and result_part.endswith('"'):
                result_part = json.loads(result_part)
                
            with open(r'data/raw_snapshots/jobs/github_careers_listing/page.html', 'w', encoding='utf-8') as fw:
                fw.write(result_part)
            
            with open(r'data/raw_snapshots/jobs/github_careers_listing/singlefile.html', 'w', encoding='utf-8') as fw:
                fw.write(result_part)
                
            print('Successfully wrote page.html and singlefile.html')
        else:
            print('Unexpected output format')
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    parse_and_save()
