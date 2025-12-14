
import json
import collections

def analyze():
    print("Analyzing backend_output.txt...")
    events = []
    try:
        with open('backend_output.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('data: '):
                    try:
                        content = line[6:].strip()
                        if content == '[DONE]': continue
                        data = json.loads(content)
                        events.append(data)
                    except Exception as e:
                        print(f"Error parsing line: {e}")
    except FileNotFoundError:
        print("File not found")
        return

    print(f"Total events found: {len(events)}")
    
    # Analyze sequences
    seq_counter = collections.Counter()
    seq_type_counter = collections.Counter()
    
    for e in events:
        if 'seq' in e:
            seq = e['seq']
            type_ = e.get('type', 'unknown')
            seq_counter[seq] += 1
            seq_type_counter[f"{seq}:{type_}"] += 1
            
            if type_ == 'audio':
                print(f"Audio Event - Seq: {seq}, Text: {e.get('text', '')[:20]}...")

    print("\nDuplicate Check:")
    duplicates_found = False
    for key, count in seq_type_counter.items():
        if count > 1:
            print(f"DUPLICATE FOUND: {key} appears {count} times!")
            duplicates_found = True
            
    if not duplicates_found:
        print("No duplicates found in backend output. Backend is CLEAN.")
    else:
        print("Backend is sending DUPLICATE events.")

if __name__ == "__main__":
    analyze()
