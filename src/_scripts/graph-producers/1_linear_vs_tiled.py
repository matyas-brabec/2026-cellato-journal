import os
import sys
import shutil
import matplotlib.pyplot as plt
import numpy as np

# --- 0. LaTeX Font Configuration & Fallback Logic ---
# Check if LaTeX is installed on the system
def has_latex():
    # checking for latex and dvipng which are typically needed by matplotlib
    return shutil.which("latex") is not None and shutil.which("dvipng") is not None

USE_LATEX = has_latex()

if USE_LATEX:
    print("LaTeX detected! Applying new LaTeX formatting and styles.")
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
    })
else:
    print("LaTeX not detected. Falling back to the older legacy style.")
    plt.rcParams.update({
        "text.usetex": False
    })

# --- 1. Data Loading ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from abstractions.results_abstractions import CSVLoader

AUTOMATA=[
    "game-of-life",
    "maze",
    "brian",
    "forest-fire",
    "wire",
    "excitable",
    "cyclic",
    "fluid",
    "critters",
    "traffic",
]

if len(sys.argv) > 2 and sys.argv[2].endswith(('.png', '.pdf')):
    path_to_csv = sys.argv[1]
    output_path = sys.argv[2]
else:
    raise Exception("Please provide the path to the CSV file and the output path as command-line arguments.")

size=16384
loader = CSVLoader(path_to_csv)
size_group = loader.get_groups_by_sizes([size**2])[size**2]
print(f"Total results for size {size}x{size}: {len(size_group)}")

# --- Implementation definitions ---
bit_planes_linear_impl = {'traverser': 'simple', 'evaluator': 'bit_planes', 'layout': 'bit_planes'}
bit_planes_tiled_impl = {'traverser': 'simple', 'evaluator': 'tiled_bit_planes', 'layout': 'tiled_bit_planes'}
temporal_linear_impl = {'traverser': 'temporal', 'evaluator': 'bit_planes', 'layout': 'bit_planes'}
temporal_tiled_impl = {'traverser': 'temporal', 'evaluator': 'tiled_bit_planes', 'layout': 'tiled_bit_planes'}

# --- Group results ---
bit_planes_linear_group = [x for x in size_group if x.is_implementation(bit_planes_linear_impl)]
bit_planes_tiled_group = [x for x in size_group if x.is_implementation(bit_planes_tiled_impl)]
temporal_linear_group = [x for x in size_group if x.is_implementation(temporal_linear_impl)]
temporal_tiled_group = [x for x in size_group if x.is_implementation(temporal_tiled_impl)]

# --- Find the best time for each implementation ---
bests_by_automaton = {}
for automaton in AUTOMATA:
    bpl_best = min([x for x in bit_planes_linear_group if x.values.get('automaton') == automaton], key=lambda x: x.normalized_time())
    bpt_best = min([x for x in bit_planes_tiled_group if x.values.get('automaton') == automaton], key=lambda x: x.normalized_time())
    tl_best = min([x for x in temporal_linear_group if x.values.get('automaton') == automaton], key=lambda x: x.normalized_time())
    tt_best = min([x for x in temporal_tiled_group if x.values.get('automaton') == automaton], key=lambda x: x.normalized_time())

    bests_by_automaton[automaton] = {
        'bit_planes_linear': bpl_best.normalized_time() * 1e9,
        'bit_planes_tiled': bpt_best.normalized_time() * 1e9,
        'temporal_linear': tl_best.normalized_time() * 1e9,
        'temporal_tiled': tt_best.normalized_time() * 1e9
    }
print("Finished processing data. Starting plot generation.")

# --- 2. Plotting Phase ---
automaton_names = {
    "game-of-life": "GoL", "forest-fire": "fire", "wire": "wire",
    "excitable": "excitable", "brian": "brian", "cyclic": "cyclic",
    "traffic": "traffic", "fluid": "fluid", "maze": "maze", "critters": "critters"
}

# Graph Configuration (Dynamically merged)
scale = 0.75 if USE_LATEX else 0.6
plot_config = {
    'y_axis_scale': 'linear',
    'figure_size': (16*scale, 6*scale),
    'bar_width': 0.18,
    'group_gap': 0.02,
    'title': f'Linear vs. Tiled Throughput for ${size}\\times{size}$ Grid' if USE_LATEX else f'Linear vs. Tiled Throughput for {size}x{size} Grid',
    'add_data_labels': False,
    
    # --- FONT SIZE CONTROLS ---
    'axis_label_fontsize': 16 if USE_LATEX else None,
    'tick_label_fontsize': 14 if USE_LATEX else None,
    'legend_fontsize': 12 if USE_LATEX else None,

    # --- CONDITIONAL COLORS & HATCHES ---
    'custom_colors': {
        'bit_planes_linear': '#A0C4FF' if USE_LATEX else '#6baed6',
        'bit_planes_tiled':  '#2C5F9C' if USE_LATEX else '#08519c',
        'temporal_linear':   '#BBF7C3' if USE_LATEX else '#74c476',
        'temporal_tiled':    '#2E8B57' if USE_LATEX else '#006d2c'
    },
    'bar_hatches': {
        'bit_planes_linear': '..' if USE_LATEX else '/',
        'bit_planes_tiled':  '///' if USE_LATEX else '//',
        'temporal_linear':   'xx' if USE_LATEX else 'x',
        'temporal_tiled':    'O' if USE_LATEX else 'xx'
    }
}

# --- Data Preparation ---
labels = [automaton_names.get(a, a) for a in AUTOMATA]
implementations = ['bit_planes_linear', 'bit_planes_tiled', 'temporal_linear', 'temporal_tiled']
impl_display_names = {
    'bit_planes_linear': 'Bit Planes (Linear)', 'bit_planes_tiled': 'Bit Planes (Tiled)',
    'temporal_linear': 'Temporal (Linear)', 'temporal_tiled': 'Temporal (Tiled)'
}
data = {impl: [] for impl in implementations}

y_axis_label = r"Throughput ($10^{12}$ Cells / Sec)" if USE_LATEX else "Throughput (10$^{12}$ Cell Updates Per Second)"
for automaton in AUTOMATA:
    for impl in implementations:
        time_in_ps = bests_by_automaton[automaton][impl]
        throughput_tcups = 1 / time_in_ps if time_in_ps > 0 else 0
        data[impl].append(throughput_tcups)

# --- ADDING GEOMETRIC MEAN ---
labels.append(r"\textbf{Geo Mean}" if USE_LATEX else "Geo Mean")
for impl in implementations:
    valid_data = [v for v in data[impl] if v > 0]
    g_mean = np.exp(np.mean(np.log(valid_data))) if valid_data else 0
    data[impl].append(g_mean)


# --- Plotting ---
fig, ax = plt.subplots(figsize=plot_config['figure_size'])

# --- APPLYING THE CUSTOM GAP (or regular spacing for legacy style) ---
num_automata = len(AUTOMATA)
gap_size = 0.6 if USE_LATEX else 0.0
x = np.append(np.arange(num_automata), num_automata + gap_size)

width = plot_config['bar_width']
gap = plot_config['group_gap']
offsets = {
    'bit_planes_linear': -1.5*width - gap, 'bit_planes_tiled': -0.5*width - gap,
    'temporal_linear': 0.5*width + gap, 'temporal_tiled': 1.5*width + gap
}

for impl in implementations:
    color = plot_config['custom_colors'].get(impl)
    hatch = plot_config['bar_hatches'].get(impl)
    
    edgecolor = 'black' if USE_LATEX else 'white'
    linewidth = 0.75 if USE_LATEX else None
    
    ax.bar(x + offsets[impl], data[impl], width, label=impl_display_names[impl], 
           color=color, hatch=hatch, edgecolor=edgecolor, linewidth=linewidth)

# --- Styling and Customization ---
# If using the old style (fontsize is None), it will gracefully fall back to matplotlib defaults
ax.set_ylabel(y_axis_label, fontsize=plot_config['axis_label_fontsize'])
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=plot_config['tick_label_fontsize'])
ax.tick_params(axis='y', labelsize=plot_config['tick_label_fontsize'])
ax.set_yscale(plot_config['y_axis_scale'])

ax.grid(axis='y', linestyle='--', alpha=0.6 if USE_LATEX else 0.7)

# Apply specialized styling if in LaTeX mode
if USE_LATEX:
    ax.spines[['top', 'right']].set_visible(False)

    # Add a subtle vertical line to separate individual automata from the Geometric Mean
    separator_x = (num_automata - 1 + x[-1]) / 2
    ax.axvline(x=separator_x, color='gray', linestyle=':', alpha=0.5)

ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.1)

ax.legend(loc='upper left', frameon=True, fontsize=plot_config['legend_fontsize'])
fig.tight_layout()

# --- Saving ---
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Graph successfully saved as {output_path}")