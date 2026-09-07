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

baseline_impl = {'reference_impl': 'baseline'}
bit_array_impl = {'traverser': 'simple', 'evaluator': 'bit_array', 'layout': 'bit_array'}
bit_planes_linear = {'traverser': 'simple', 'evaluator': 'bit_planes', 'layout': 'bit_planes'}
bit_planes_tiled = {'traverser': 'simple', 'evaluator': 'tiled_bit_planes', 'layout': 'tiled_bit_planes'}
temporal_linear = {'traverser': 'temporal', 'evaluator': 'bit_planes', 'layout': 'bit_planes'}
temporal_tiled = {'traverser': 'temporal', 'evaluator': 'tiled_bit_planes', 'layout': 'tiled_bit_planes'}

baseline_group = [x for x in size_group if x.is_implementation(baseline_impl)]
bit_array_group = [x for x in size_group if x.is_implementation(bit_array_impl)]
bit_planes_group = [x for x in size_group if x.is_implementation(bit_planes_linear) or x.is_implementation(bit_planes_tiled)]
temporal_group = [x for x in size_group if x.is_implementation(temporal_linear) or x.is_implementation(temporal_tiled)]

bests_by_automaton = {}
for automaton in AUTOMATA:
    print(f"Processing automaton: {automaton}")
    baseline_for_automaton = [x for x in baseline_group if x.values.get('automaton') == automaton]
    bit_array_for_automaton = [x for x in bit_array_group if x.values.get('automaton') == automaton]
    bit_planes_for_automaton = [x for x in bit_planes_group if x.values.get('automaton') == automaton]
    temporal_for_automaton = [x for x in temporal_group if x.values.get('automaton') == automaton]

    baseline_best = min(baseline_for_automaton, key=lambda x: x.normalized_time())
    bit_array_best = min(bit_array_for_automaton, key=lambda x: x.normalized_time())
    bit_planes_best = min(bit_planes_for_automaton, key=lambda x: x.normalized_time())
    temporal_best = min(temporal_for_automaton, key=lambda x: x.normalized_time())

    bests_by_automaton[automaton] = {
        'baseline': baseline_best.normalized_time() * 1e9,
        'bit_array': bit_array_best.normalized_time() * 1e9,
        'bit_planes': bit_planes_best.normalized_time() * 1e9,
        'temporal': temporal_best.normalized_time() * 1e9
    }
print("Finished processing data. Starting plot generation.")


# --- 2. Plotting Phase ---
automaton_names = {
    "game-of-life": "GoL", "forest-fire": "fire", "wire": "wire",
    "excitable": "excitable", "brian": "brian", "cyclic": "cyclic",
    "traffic": "traffic", "fluid": "fluid", "maze": "maze", "critters": "critters"
}

# Graph Configuration (Dynamically merged)
scale = 0.8 if USE_LATEX else 0.9
plot_config = {
    'y_axis_mode': 'speedup',
    'y_axis_scale': 'log', # possible values: 'linear', 'log'
    'figure_size': (16*scale, 6*scale),
    'bar_width': 0.18 if USE_LATEX else 0.2,
    'title': f'Performance Comparison for ${size}\\times{size}$ Grid' if USE_LATEX else f'Performance Comparison for {size}x{size} Grid',
    'show_baseline_bar': False,
    'show_baseline_line': True,
    'add_data_labels': False,

    # --- FONT SIZE CONTROLS ---
    'title_fontsize': 20,
    'axis_label_fontsize': 16,
    'tick_label_fontsize': 14,
    'legend_fontsize': 14,
    'data_label_fontsize': 10,

    'label_use_background': True,
    'label_rotation': 45,
    'label_padding': 3,
    
    # Conditionally load colors
    'custom_colors': {
        'baseline': '#003f5c',
        'bit_array': '#6baed6' if USE_LATEX else '#1f77b4',
        'bit_planes': '#74c476' if USE_LATEX else '#2ca02c',
        'temporal': '#fd8d3c' if USE_LATEX else '#ff7f0e'
    },
    
    # Conditionally load hatches
    'bar_hatches': {
        'baseline': '/',
        'bit_array': '..' if USE_LATEX else '\\',
        'bit_planes': '///' if USE_LATEX else '.',
        'temporal': 'xx' if USE_LATEX else 'o'
    },
    'hatch_density': 0.5
}


# --- Data Preparation ---
labels = [automaton_names.get(a, a) for a in AUTOMATA]
implementations = ['baseline', 'bit_array', 'bit_planes', 'temporal']
impl_display_names = {
    'baseline': 'Baseline', 
    'bit_array': 'Bit-packing', 
    'bit_planes': 'Bit Planes (Linear)', 
    'temporal': 'Temporal'
}
data = {}

if not plot_config['show_baseline_bar']:
    implementations.remove('baseline')
for impl in implementations:
    data[impl] = []
    
if plot_config['y_axis_mode'] == 'speedup':
    y_axis_label = "Speedup Relative to Baseline"
    for automaton in AUTOMATA:
        baseline_time = bests_by_automaton[automaton]['baseline']
        for impl in implementations:
            data[impl].append(1.0 if impl == 'baseline' else baseline_time / bests_by_automaton[automaton][impl])
else:
    y_axis_label = "Execution Time per Cell (ps)"
    for automaton in AUTOMATA:
        for impl in implementations:
            data[impl].append(bests_by_automaton[automaton][impl])

# --- ADDING GEOMETRIC MEAN ---
labels.append(r"\textbf{Geo Mean}" if USE_LATEX else "Geo Mean")
for impl in implementations:
    # np.exp(np.mean(np.log(array))) is the mathematically stable way to compute Geometric Mean
    g_mean = np.exp(np.mean(np.log(data[impl])))
    data[impl].append(g_mean)

# Append "(log scale)" if the config is set to log and using new style
if plot_config['y_axis_scale'] == 'log' and USE_LATEX:
    y_axis_label += " (log scale)"

# --- Plotting ---
fig, ax = plt.subplots(figsize=plot_config['figure_size'])

# --- APPLYING THE CUSTOM GAP (or regular spacing for legacy style) ---
num_automata = len(AUTOMATA)
gap_size = 0.6 if USE_LATEX else 0.0
x = np.append(np.arange(num_automata), num_automata + gap_size)

width = plot_config['bar_width']
num_implementations = len(implementations)
offsets = np.linspace(-width * (num_implementations - 1) / 2, width * (num_implementations - 1) / 2, num_implementations)
bar_containers = {}

for i, impl in enumerate(implementations):
    color = plot_config['custom_colors'].get(impl)
    hatch = plot_config['bar_hatches'].get(impl)
    
    if not USE_LATEX and hatch and plot_config.get('hatch_density', 1) < 1:
        hatch = hatch[0]
        
    edgecolor = 'black' if USE_LATEX else None
    
    bars = ax.bar(
        x + offsets[i], 
        data[impl], 
        width, 
        label=impl_display_names[impl], 
        color=color, 
        hatch=hatch, 
        edgecolor=edgecolor
    )
    bar_containers[impl] = bars


# --- Styling and Customization ---
ax.set_ylabel(y_axis_label, fontsize=plot_config['axis_label_fontsize'])
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=plot_config['tick_label_fontsize'])
ax.tick_params(axis='y', labelsize=plot_config['tick_label_fontsize'])
ax.set_yscale(plot_config['y_axis_scale'])

# Subtlety of grid based on style mode
ax.grid(axis='y', linestyle='--', alpha=0.6 if USE_LATEX else 0.7)

# Apply specialized styling if in LaTeX mode
if USE_LATEX:
    # Removed top and right plot borders for a cleaner look
    ax.spines[['top', 'right']].set_visible(False)

    # Add a subtle vertical line to separate individual automata from the Geometric Mean
    separator_x = (num_automata - 1 + x[-1]) / 2
    ax.axvline(x=separator_x, color='gray', linestyle=':', alpha=0.5)

if plot_config['show_baseline_line'] and plot_config['y_axis_mode'] == 'speedup':
    col = 'red' 
    line_width = 1.4
    ax.axhline(y=1, color=col, linestyle='--', linewidth=line_width)
    ax.plot([], [], color=col, linestyle='--', linewidth=line_width, label='Baseline Performance (1x)')

if plot_config['add_data_labels']:
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.8) if plot_config['label_use_background'] else None
    for impl, bars in bar_containers.items():
        label_format = '%.1fx' if plot_config['y_axis_mode'] == 'speedup' else '%d'
        ax.bar_label(bars, fmt=label_format,
                         padding=plot_config['label_padding'],
                         fontsize=plot_config['data_label_fontsize'],
                         bbox=bbox_props,
                         rotation=plot_config['label_rotation'])

if plot_config['show_baseline_line'] and plot_config['y_axis_mode'] == 'speedup':
    current_ylim = ax.get_ylim()
    ax.set_ylim(bottom=min(1.0, current_ylim[0]), top=current_ylim[1] * 1.3)

# Apply the legend font size with two columns
ax.legend(loc='upper center', ncol=2, fontsize=plot_config['legend_fontsize'])
fig.tight_layout()

# --- Saving ---
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Graph successfully saved as {output_path}!")