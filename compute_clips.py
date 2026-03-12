import json

with open('all_plots.json', 'r') as f:
    plots = json.load(f)

# Left diagonal boundary equations derived from plot positions:
# Section: plots 8-15 (main left diagonal between roads)
# Computed from: plot 8 (y=55.2, x=20.47) to plot 15 (y=78.3, x=16.97)
# x = 28.833 - 0.1515 * y

def diag_left_main(y):
    return 28.833 - 0.1515 * y

# Section: plots 6-7 (upper-mid left diagonal)
# x = 22.5 - 0.1 * y
def diag_left_upper(y):
    return 22.5 - 0.1 * y

# Section: plots 1-5 (top triangle)
# x = 21.5 - 0.065 * y
def diag_left_top(y):
    return 21.5 - 0.065 * y

clip_paths = {}

for p in plots:
    lbl = p['lbl']
    top_y = p['top']
    bot_y = p['top'] + p['height']

    diag_fn = None
    if lbl in ['1', '2', '3', '4', '5']:
        diag_fn = diag_left_top
    elif lbl in ['6', '7']:
        diag_fn = diag_left_upper
    elif lbl in [str(i) for i in range(8, 16)]:
        diag_fn = diag_left_main

    if diag_fn and p['width'] > 0:
        x_at_top = diag_fn(top_y)
        x_at_bot = diag_fn(bot_y)
        tl_pct = max(0, min(100, (x_at_top - p['left']) / p['width'] * 100))
        bl_pct = max(0, min(100, (x_at_bot - p['left']) / p['width'] * 100))
        if tl_pct > 3 or bl_pct > 3:
            clip_paths[lbl] = f"polygon({tl_pct:.0f}% 0%, 100% 0%, 100% 100%, {bl_pct:.0f}% 100%)"

print("Clip paths for left-edge plots:")
for lbl in sorted(clip_paths.keys(), key=lambda x: int(x) if x.isdigit() else 999):
    print(f"  Plot {lbl}: {clip_paths[lbl]}")

# Find rightmost plots
print("\nRightmost plots:")
max_right = sorted(plots, key=lambda p: p['left'] + p['width'], reverse=True)[:15]
for p in max_right:
    r = p['left'] + p['width']
    print(f"  Plot {p['lbl']}: L={p['left']:.1f}% R={r:.1f}% T={p['top']:.1f}%")

# Right diagonal boundary
# Looking at the image, the right boundary of the layout converges to a point
# The rightmost plots descend as we go up, forming a triangle
# At bottom (~86%): right edge goes to about 74%
# At top (~8%): right edge goes to about 29% (first column)
# But the grid area between columns has different right boundaries per section

# For the RIGHT boundary, the key plots that might need clipping are:
# - Any plot whose right edge exceeds the right diagonal

# Looking at the data, the rightmost regular plots are around 74%
# These are already constrained by their width

# The right diagonal from image observation:
# At y=65%: x_right ≈ 63%
# At y=70%: x_right ≈ 69%
# At y=80%: x_right ≈ 74%
# At y=86%: x_right ≈ 76%

# Most plots are already within these bounds. Let me check if any need clipping.
# Right boundary: x_right = 10 + 0.78 * y (approximate from image)
def diag_right(y):
    # From observations: at y=65, x=63; at y=86, x=76
    # slope = (76-63)/(86-65) = 13/21 = 0.619
    # x = 63 + 0.619*(y-65) = 63 - 40.235 + 0.619*y = 22.765 + 0.619*y
    return 22.765 + 0.619 * y

print("\nRight boundary check:")
for p in plots:
    r = p['left'] + p['width']
    top_y = p['top']
    bot_y = top_y + p['height']
    rb_top = diag_right(top_y)
    rb_bot = diag_right(bot_y)
    if r > rb_top + 1 or r > rb_bot + 1:
        print(f"  Plot {p['lbl']}: R={r:.1f}% exceeds boundary ({rb_top:.1f}%-{rb_bot:.1f}%) at y={top_y:.1f}%")

# Save clip_paths for HTML generation
with open('clip_paths.json', 'w') as f:
    json.dump(clip_paths, f, indent=2)
print(f"\nSaved {len(clip_paths)} clip paths")
