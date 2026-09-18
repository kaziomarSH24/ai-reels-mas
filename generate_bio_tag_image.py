import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

words = ['The', 'new', 'design', 'is', 'quite', 'piece', 'of', 'cake', 'compared', 'to', 'the', 'old', 'one', '.']
tags =  [0,     0,     0,        0,    0,       1,       2,    2,      0,          0,    0,     0,     0,     0]
labels = ['O', 'O', 'O', 'O', 'O', 'B-IDIOM', 'I-IDIOM', 'I-IDIOM', 'O', 'O', 'O', 'O', 'O', 'O']

fig, ax = plt.subplots(figsize=(15, 3))
ax.axis('off')

# Colors
color_O = '#f1f5f9' # Light slate
color_B = '#fde047' # Bright Yellow (Highlight)
color_I = '#fef08a' # Lighter Yellow

start_x = 0
box_width = 1.2
box_height = 0.6
spacing = 0.1

for i, (w, t, l) in enumerate(zip(words, tags, labels)):
    c = color_O
    edge = '#cbd5e1'
    if t == 1: 
        c = color_B
        edge = '#eab308'
    if t == 2: 
        c = color_I
        edge = '#facc15'
    
    # Draw Rectangle (Border radius not natively supported in standard patches Rectangle without boxstyle, but simple is fine)
    rect = patches.Rectangle((start_x, 0), box_width, box_height, linewidth=2, edgecolor=edge, facecolor=c)
    ax.add_patch(rect)
    
    # Add Word text
    plt.text(start_x + box_width/2, box_height/2 + 0.15, w, ha='center', va='center', fontsize=12, fontweight='bold', color='#1e293b')
    
    # Add Tag Label below word
    plt.text(start_x + box_width/2, box_height/2 - 0.15, l, ha='center', va='center', fontsize=9, fontweight='bold', color='#64748b')
    
    # Add integer tag at the bottom
    plt.text(start_x + box_width/2, -0.2, f"[{t}]", ha='center', va='center', fontsize=15, fontweight='bold', color='#ef4444' if t>0 else '#94a3b8')
    
    start_x += box_width + spacing

ax.set_xlim(-0.2, start_x)
ax.set_ylim(-0.5, 1.0)

plt.title("DistilBERT NLP Tokenization & BIO Tagging (Word-to-Integer Mapping)", fontsize=18, fontweight='bold', pad=15, color='#0f172a')

output_path = '/var/www/bio_tagging_visual.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
