import os
import sys
import shutil
import matplotlib.pyplot as plt
import numpy as np

# --- 0. LaTeX Font Configuration & Fallback Logic ---
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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from abstractions.results_abstractions import CSVLoader

AUTOMATA = [
    "game-of-life", "maze", "critters",     # 1-bit
    "brian", "forest-fire", "wire", "traffic", # 2-bit
    "excitable",                            # 3-bit
    "fluid",                                # 4-bit
    "cyclic"                                # 5-bit
]

AUTOMATA_BITS = {
    "game-of-life": 1, "maze": 1, "critters": 1,
    "brian": 2, "forest-fire": 2, "wire": 2, "traffic": 2,
    "excitable": 3,
    "fluid": 4,
    "cyclic": 5
}

if len(sys.argv) > 2 and sys.argv[2].endswith(('.png', '.pdf')):
    path_to_csv = sys.argv[1]
    output_path = sys.argv[2]
else:
    raise Exception("Usage: python plot_efficiency_vs_ceiling.py <path_to_csv> <output_path.png/pdf>")

size = 16384
loader = CSVLoader(path_to_csv)
size_group = loader.get_groups_by_sizes([size**2])[size**2]
print(f"Total results for size {size}x{size}: {len(size_group)}")

# --- Implementation Definitions ---
IMPLS = {
    'baseline': {'reference_impl': 'baseline'},
    'bit_array': {'traverser': 'simple', 'evaluator': 'bit_array', 'layout': 'bit_array'},
    'spatial_linear': {'traverser': 'simple', 'evaluator': 'bit_planes', 'layout': 'bit_planes'},
    'temporal_linear': {'traverser': 'temporal', 'evaluator': 'bit_planes', 'layout': 'bit_planes'},
    'temporal_tiled': {'traverser': 'temporal', 'evaluator': 'tiled_bit_planes', 'layout': 'tiled_bit_planes'}
}

# --- Extract Theoretical Ceilings Per Implementation ---
ceilings = {b: {} for b in range(1, 6)}

for bits in range(1, 6):
    copy_name = f"copy--max-throughput-estimate--{bits}-bit"
    copy_results = [x for x in size_group if x.values.get('automaton') == copy_name]
    
    if copy_results:
        for impl_name, impl_dict in IMPLS.items():
            impl_copy_results = [x for x in copy_results if x.is_implementation(impl_dict)]
            if impl_copy_results:
                best_copy = min(x.normalized_time() for x in impl_copy_results)
                ceilings[bits][impl_name] = best_copy * 1e9
            else:
                ceilings[bits][impl_name] = None
    else:
        for impl_name in IMPLS.keys():
            ceilings[bits][impl_name] = None

# --- Extract Best Times & Calculate Efficiency ---
plot_categories = ['baseline', 'bit_array', 'spatial_linear', 'best_temporal']
efficiency_data = {cat: [] for cat in plot_categories}
valid_automata = []

for automaton in AUTOMATA:
    req_bits = AUTOMATA_BITS[automaton]
    if not any(ceilings[req_bits].values()):
        continue 
        
    valid_automata.append(automaton)
    automaton_results = [x for x in size_group if x.values.get('automaton') == automaton]
    
    # 1. Baseline
    base_res = [x for x in automaton_results if x.is_implementation(IMPLS['baseline'])]
    if base_res and ceilings[req_bits].get('baseline'):
        base_time = min(x.normalized_time() * 1e9 for x in base_res)
        efficiency_data['baseline'].append((ceilings[req_bits]['baseline'] / base_time) * 100)
    else:
        efficiency_data['baseline'].append(0)

    # 2. Bit Array (Bit-packing)
    ba_res = [x for x in automaton_results if x.is_implementation(IMPLS['bit_array'])]
    if ba_res and ceilings[req_bits].get('bit_array'):
        ba_time = min(x.normalized_time() * 1e9 for x in ba_res)
        efficiency_data['bit_array'].append((ceilings[req_bits]['bit_array'] / ba_time) * 100)
    else:
        efficiency_data['bit_array'].append(0)

    # 3. Spatial Bit Planes (Linear)
    spat_res = [x for x in automaton_results if x.is_implementation(IMPLS['spatial_linear'])]
    if spat_res and ceilings[req_bits].get('spatial_linear'):
        spat_time = min(x.normalized_time() * 1e9 for x in spat_res)
        efficiency_data['spatial_linear'].append((ceilings[req_bits]['spatial_linear'] / spat_time) * 100)
    else:
        efficiency_data['spatial_linear'].append(0)

    # 4. Best Temporal Configuration
    temp_lin_res = [x for x in automaton_results if x.is_implementation(IMPLS['temporal_linear'])]
    temp_til_res = [x for x in automaton_results if x.is_implementation(IMPLS['temporal_tiled'])]
    
    t_lin_time = min((x.normalized_time() * 1e9 for x in temp_lin_res), default=float('inf'))
    t_til_time = min((x.normalized_time() * 1e9 for x in temp_til_res), default=float('inf'))
    
    if t_lin_time == float('inf') and t_til_time == float('inf'):
        efficiency_data['best_temporal'].append(0)
    elif t_lin_time < t_til_time:
        ceiling = ceilings[req_bits].get('temporal_linear', 0)
        eff = (ceiling / t_lin_time) * 100 if ceiling else 0
        efficiency_data['best_temporal'].append(eff)
    else:
        ceiling = ceilings[req_bits].get('temporal_tiled', 0)
        eff = (ceiling / t_til_time) * 100 if ceiling else 0
        efficiency_data['best_temporal'].append(eff)

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
    'figure_size': (16*scale, 6*scale),
    'bar_width': 0.18 if USE_LATEX else 0.2,
    
    # --- FONT SIZE CONTROLS ---
    'axis_label_fontsize': 16 if USE_LATEX else 12,
    'tick_label_fontsize': 14 if USE_LATEX else 11,
    'legend_fontsize': 13 if USE_LATEX else 11,
    
    # Colors aligned with your primary performance script
    'custom_colors': {
        'baseline': '#003f5c',
        'bit_array': '#6baed6' if USE_LATEX else '#1f77b4',
        'spatial_linear': '#74c476' if USE_LATEX else '#2ca02c',
        'best_temporal': '#fd8d3c' if USE_LATEX else '#ff7f0e'
    },
    'bar_hatches': {
        'baseline': '/',
        'bit_array': '..' if USE_LATEX else '\\',
        'spatial_linear': '///' if USE_LATEX else '.',
        'best_temporal': 'xx' if USE_LATEX else 'o'
    }
}

labels = [automaton_names.get(a, a) for a in valid_automata]
display_names = {
    'baseline': 'Baseline',
    'spatial_linear': 'Bit Planes (Linear)',
    'best_temporal': 'Temporal Bit Planes (Linear/Tiled)',
    'bit_array': 'Bit-packing'
}

# --- ADDING GEOMETRIC MEAN ---
labels.append(r"\textbf{Geo Mean}" if USE_LATEX else "Geo Mean")
for cat in plot_categories:
    valid_data = [v for v in efficiency_data[cat] if v > 0]
    g_mean = np.exp(np.mean(np.log(valid_data))) if valid_data else 0
    efficiency_data[cat].append(g_mean)

# --- Apply layout and calculate X positions ---
fig, ax = plt.subplots(figsize=plot_config['figure_size'])

num_items = len(valid_automata)
gap_size = 0.6 if USE_LATEX else 0.0
x = np.append(np.arange(num_items), num_items + gap_size)

width = plot_config['bar_width']
num_implementations = len(plot_categories)
offsets = np.linspace(-width * (num_implementations - 1) / 2, width * (num_implementations - 1) / 2, num_implementations)

for i, cat in enumerate(plot_categories):
    color = plot_config['custom_colors'].get(cat)
    hatch = plot_config['bar_hatches'].get(cat)
    edgecolor = 'black' if USE_LATEX else None
    
    ax.bar(
        x + offsets[i], 
        efficiency_data[cat], 
        width, 
        label=display_names[cat], 
        color=color, 
        hatch=hatch, 
        edgecolor=edgecolor, 
        alpha=0.9
    )

# --- Styling and Customization ---
y_axis_label = r"Memory Bandwidth Saturation (\%)" if USE_LATEX else "Memory Bandwidth Saturation (%)"
ax.set_ylabel(y_axis_label, fontsize=plot_config['axis_label_fontsize'], fontweight='bold' if not USE_LATEX else 'normal')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=plot_config['tick_label_fontsize'])
ax.tick_params(axis='y', labelsize=plot_config['tick_label_fontsize'])
ax.grid(axis='y', linestyle='--', alpha=0.6 if USE_LATEX else 0.7)

# Apply specialized styling if in LaTeX mode
if USE_LATEX:
    ax.spines[['top', 'right']].set_visible(False)
    
    # Add a subtle vertical line to separate individual automata from the Geometric Mean
    separator_x = (num_items - 1 + x[-1]) / 2
    ax.axvline(x=separator_x, color='gray', linestyle=':', alpha=0.5)

# The 100% limit line
ax.axhline(y=100, color='black', linestyle='-', linewidth=1.5, zorder=0)
bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1)
limit_text = r"\textbf{100\% = Memory Limit For Selected Impl.}" if USE_LATEX else "100% = Memory Limit For Selected Implementation"
ax.text(x=-0.4, y=96, s=limit_text, color="black", 
        fontsize=10, fontweight='bold', ha='left', va='top', bbox=bbox_props)

ax.set_ylim(bottom=0, top=105)
ax.set_yticks([0, 20, 40, 60, 80, 100])

# Add legend
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15 if USE_LATEX else -0.12), ncol=4, fontsize=plot_config['legend_fontsize'])
fig.tight_layout()

# --- Saving ---
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Efficiency graph successfully saved as {output_path}")