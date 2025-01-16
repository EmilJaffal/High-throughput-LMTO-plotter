import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import re

# Define transition metals
transition_metals = [
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
    "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"
]

# Define the Mendeleev number mapping
mendeleev_numbers = {
    "H": 92, "He": 98, "Li": 1, "Be": 67, "B": 72, "C": 77, "N": 82, "O": 87, "F": 93, "Ne": 99,
    "Na": 2, "Mg": 68, "Al": 73, "Si": 78, "P": 83, "S": 88, "Cl": 94, "Ar": 100, "K": 3, "Ca": 7,
    "Sc": 11, "Ti": 43, "V": 46, "Cr": 49, "Mn": 52, "Fe": 55, "Co": 58, "Ni": 61, "Cu": 64, "Zn": 69,
    "Ga": 74, "Ge": 79, "As": 84, "Se": 89, "Br": 95, "Kr": 101, "Rb": 4, "Sr": 8, "Y": 12, "Zr": 44,
    "Nb": 47, "Mo": 50, "Tc": 53, "Ru": 56, "Rh": 59, "Pd": 62, "Ag": 65, "Cd": 70, "In": 75,
    "Sn": 80, "Sb": 85, "Te": 90, "I": 96, "Xe": 102, "Cs": 5, "Ba": 9, "La": 13, "Ce": 15,
    "Pr": 17, "Nd": 19, "Pm": 21, "Sm": 23, "Eu": 25, "Gd": 27, "Tb": 29, "Dy": 31, "Ho": 33,
    "Er": 35, "Tm": 37, "Yb": 39, "Lu": 41, "Hf": 45, "Ta": 48, "W": 51, "Re": 54, "Os": 57,
    "Ir": 60, "Pt": 63, "Au": 66, "Hg": 71, "Tl": 76, "Pb": 81, "Bi": 86, "Po": 91, "At": 97,
    "Rn": 103, "Fr": 6, "Ra": 10, "Ac": 14, "Th": 16, "Pa": 18, "U": 20, "Np": 22, "Pu": 24,
    "Am": 26, "Cm": 28, "Bk": 30, "Cf": 32, "Es": 34, "Fm": 36, "Md": 38, "No": 40, "Lr": 42,
}

def get_dos_files(folder_path):
    return glob.glob(os.path.join(folder_path, 'DOS-*.csv'))

def extract_elements(label):
    return re.findall(r'[A-Z][a-z]?', label)

def get_element_color(label, elements):
    if label.lower() == 'total':
        return 'black', '-'
    if label.lower() == 'e':
        return 'darkgrey', '--'
    elements = [e for e in elements if e.lower() != 'e']
    element_count = len(elements)
    if element_count == 1:
        return 'blue', '-'
    elif element_count == 2:
        return ('blue', '-') if label == elements[0] else ('red', '-')
    elif element_count == 3:
        if label == elements[0]:
            return 'blue', '-'
        elif label in transition_metals:
            return 'grey', '-'
        elif label == elements[2]:
            return 'red', '-'
    elif element_count == 4:
        if label == elements[0]:
            return 'blue', '-'
        elif label in transition_metals:
            return 'grey', '-'
        elif label == elements[2]:
            return 'green', '-'
        elif label == elements[3]:
            return 'red', '-'
    return 'black', '-'

def plot_dos(folder_path):
    def plot(include_e):
        dos_files = get_dos_files(folder_path)
        if not dos_files:
            print("No DOS files found in the directory.")
            return

        fig, ax = plt.subplots(figsize=(8, 15))
        all_y_values = []
        all_elements = []

        file_data = []
        for filename in dos_files:
            data = pd.read_csv(filename, sep=',', skiprows=1, header=None)
            data.columns = ['Energy', 'DOS', 'Intg_DOS']
            data['Energy'] = pd.to_numeric(data['Energy'], errors='coerce')
            data['DOS'] = pd.to_numeric(data['DOS'], errors='coerce')
            data['Intg_DOS'] = pd.to_numeric(data['Intg_DOS'], errors='coerce')

            x = data['Energy'].values
            y = data['DOS'].values
            all_y_values.extend(y[(x >= -8) & (x <= 2)])

            label = os.path.splitext(os.path.basename(filename))[0].replace('DOS-', '')
            elements = extract_elements(label)
            all_elements.extend(elements)
            file_data.append((x, y, label))

        all_elements = list(set(all_elements))
        sorted_elements = sorted(all_elements, key=lambda e: mendeleev_numbers.get(e, float('inf')))
        max_y = max(all_y_values)
        buffer = 0.1 * max_y

        def sort_key(item):
            label = item[2]
            if label.lower() == "total":
                return (-1, 0)
            if label == "E" and not include_e:
                return (float('inf'), float('inf'))
            return (mendeleev_numbers.get(label, float('inf')), label)

        file_data.sort(key=sort_key)

        for x, y, label in file_data:
            if label.lower() == 'e' and not include_e:
                continue
            elements = extract_elements(label)
            color, linestyle = get_element_color(label, sorted_elements)
            zorder_value = 10 if label.lower() == 'total' else 0
            ax.plot(y, x, label=label, color=color, linewidth=5, linestyle=linestyle, zorder=zorder_value)

        ax.set_ylim(-8, 2)
        ax.set_xlim(0, max_y + buffer)
        ax.axhline(0, color='black', linestyle='--', linewidth=3)
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        ax.tick_params(axis='y', labelsize=35, width=3, length=10)

        for spine in ax.spines.values():
            spine.set_linewidth(2.5)

        ax.set_ylabel('energy, eV', fontsize=35)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend(frameon=False, fontsize=30, loc='lower right', handlelength=0.75, columnspacing=0.1)

        folder_name = os.path.basename(folder_path).split('-')[0]
        folder_name_subscripted = re.sub(r'(\d+)', lambda x: r'$_\mathrm{' + x.group(0) + r'}$', folder_name)
        ax.set_title(folder_name_subscripted + ' DOS', fontsize=35, pad=20)

        x_position = ax.get_xlim()[1]
        ax.annotate(
            r'$E_{\mathrm{F}}$',
            xy=(x_position, 0),
            xytext=(10, 0),
            textcoords='offset points',
            fontsize=35,
            va='center',
            ha='left',
            color='black'
        )

        plt.tight_layout()

        if include_e:
            output_filename = os.path.join(folder_path, f"{os.path.basename(folder_path)}_DOS.png")
        else:
            output_filename = os.path.join(folder_path, f"{os.path.basename(folder_path)}_DOS_noE.png")
        
        plt.savefig(output_filename, dpi=300)

        print(f"Plot saved to: {output_filename}")
        plt.close(fig)  # Close the figure to avoid too many open figures

    plot(include_e=True)
    plot(include_e=False)


def plot_bandstructure(folder_path):
    points_file = os.path.join(folder_path, 'band_structure_points.csv')
    band_file = os.path.join(folder_path, 'band_structure.csv')

    if not (os.path.exists(points_file) and os.path.exists(band_file)):
        print("Band structure files not found in:", folder_path)
        return

    points_data = pd.read_csv(points_file, delimiter=',')
    points_data.columns = points_data.columns.str.strip()

    band_data = pd.read_csv(band_file, delimiter=',')
    band_data.columns = band_data.columns.str.strip()

    ticks = points_data['values'].tolist()
    labels = points_data['point'].tolist()

    folder_name = os.path.basename(folder_path).split('-')[0]
    folder_name_subscripted = re.sub(r'(\d+)', lambda x: r'$_\mathrm{' + x.group(0) + r'}$', folder_name)

    x_min = min(ticks)
    x_max = max(ticks)

    plt.rcParams.update({'font.size': 20, 'axes.labelsize': 20, 'xtick.labelsize': 20, 'ytick.labelsize': 20})

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(band_data['k'], band_data['Energy (eV)'], color='blue', linewidth=0.85, zorder=1)

    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    ax.set_xlabel('k-points')
    ax.set_ylabel('energy, eV', labelpad=-5)

    ax.set_title(folder_name_subscripted + ' band structure', fontsize=20, pad=10)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(-2.5, 2.5)
    ax.axhline(0, color='black', linewidth=1.5, linestyle='--', zorder=1)

    x_position = ax.get_xlim()[1]
    ax.annotate(
        r'$E_{\mathrm{F}}$',
        xy=(x_position, 0),
        xytext=(10, 0),
        textcoords='offset points',
        fontsize=20,
        va='center',
        ha='left',
        color='black',
        zorder=1
    )

    ax.grid(axis='x', color='black', alpha=1, zorder=2, linewidth=1.5)

    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    ax.tick_params(axis='both', width=1.5, length=8)

    plt.tight_layout()

    save_path = os.path.join(folder_path, f'{folder_name}_bandstructure.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')

    print(f"Plot saved to: {save_path}")
    plt.close(fig)  

def main():
    parent_folder = input("Enter the directory path: ").strip()
    process_multiple = input("Would you like to process a folder of different structures? (y/n): ").strip().lower()

    if process_multiple == 'y':
        choice = input("Choose an option for all folders: 1. Plot DOS, 2. Plot band structure, 3. Plot all of the above: ").strip()
        for folder_name in os.listdir(parent_folder):
            folder_path = os.path.join(parent_folder, folder_name)
            if os.path.isdir(folder_path):
                print(f"Processing folder: {folder_path}")
                if choice == "1":
                    plot_dos(folder_path)
                elif choice == "2":
                    plot_bandstructure(folder_path)
                elif choice == "3":
                    plot_dos(folder_path)
                    plot_bandstructure(folder_path)
                else:
                    print("Invalid choice.")
                    break
    else:
        choice = input("Choose an option: 1. Plot DOS, 2. Plot band structure, 3. Plot all of the above: ").strip()
        if choice == "1":
            plot_dos(parent_folder)
        elif choice == "2":
            plot_bandstructure(parent_folder)
        elif choice == "3":
            plot_dos(parent_folder)
            plot_bandstructure(parent_folder)
        else:
            print("Invalid choice.")

    print("teehee tnx!")
    exit()

if __name__ == "__main__":
    main()