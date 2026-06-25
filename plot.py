import pandas as pd
import matplotlib.pyplot as plt
from genetic_algorithm import *

def plot_single_file(file_name, subtitle, xlim, ylim):
    df = pd.read_csv(file_name, sep=';')
    df['store_avg'] = df['store_avg'].str.replace(',', '.').astype(float)
    df['retrieve_avg'] = df['retrieve_avg'].str.replace(',', '.').astype(float)
    _, ax1 = plt.subplots(figsize=(10,5))
    ax1.scatter(df['store_avg'], df['retrieve_avg'], color="#009900", s=60, alpha=0.90, edgecolors='black', linewidth=0.5, marker='s')
    ax1.set_xlabel('Average storage flow time (s)', fontsize=15, fontweight='bold')
    ax1.set_ylabel('Average retrieval flow time (s)', fontsize=15, fontweight='bold')
    ax1.tick_params(axis='x', labelsize=12)
    ax1.tick_params(axis='y', labelsize=12)
    ax1.set_title(f'Average storage flow time x Average retrieval flow time - {subtitle}', fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    if xlim is not None: plt.xlim(xlim)
    if ylim is not None: plt.ylim(ylim)
    plt.tight_layout()

def plot_two_files(file_name1, file_name2, subtitle, xlim, ylim, label1='File 1', label2='File 2'):
    def load_file(file_name):
        df = pd.read_csv(file_name, sep=';')
        df['store_avg'] = df['store_avg'].str.replace(',', '.').astype(float)
        df['retrieve_avg'] = df['retrieve_avg'].str.replace(',', '.').astype(float)
        return df
    df1 = load_file(file_name1)
    df2 = load_file(file_name2)
    _, ax1 = plt.subplots(figsize=(10,5))
    ax1.scatter(df1['store_avg'], df1['retrieve_avg'], color="#009900", s=50, alpha=0.80, edgecolors='black', linewidth=0.5, marker='s',label=f'{label1}')
    ax1.scatter(df2['store_avg'], df2['retrieve_avg'], color="#FF6600", s=50, alpha=0.80, edgecolors='black', linewidth=0.5, marker='^',label=f'{label2}')
    ax1.set_xlabel('Average storage flow time (s)', fontsize=15, fontweight='bold')
    ax1.set_ylabel('Average retrieval flow time (s)', fontsize=15, fontweight='bold')
    ax1.tick_params(axis='x', labelsize=12)
    ax1.tick_params(axis='y', labelsize=12)
    ax1.set_title(f'Average storage flow time x Average retrieval flow time - {subtitle}', fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='best', fontsize=9, ncol=1)
    if xlim is not None: plt.xlim(xlim)
    if ylim is not None: plt.ylim(ylim)
    plt.tight_layout()

def plot_comparison(file_name1, file_name2, subtitle, xlim, ylim, label1='File 1', label2='File 2'):
    def load_file(file_name):
        df = pd.read_csv(file_name, sep=';')
        df['store_avg'] = df['store_avg'].str.replace(',', '.').astype(float)
        df['retrieve_avg'] = df['retrieve_avg'].str.replace(',', '.').astype(float)
        df['store_std'] = df['store_std'].str.replace(',', '.').astype(float)
        df['retrieve_std'] = df['retrieve_std'].str.replace(',', '.').astype(float)
        return df
    def classify(df1, df2):
        fit1 = list(zip(df1['store_avg'], df1['retrieve_avg']))
        std1 = list(zip(df1['store_std'], df1['retrieve_std']))
        fit2 = list(zip(df2['store_avg'], df2['retrieve_avg']))
        std2 = list(zip(df2['store_std'], df2['retrieve_std']))
        df1_is_dominated = [False] * len(fit1)
        df2_is_dominated = [False] * len(fit2)
        for i, (f1, s1) in enumerate(zip(fit1, std1)):
            for j, (f2, s2) in enumerate(zip(fit2, std2)):
                if dominates_stochastic(f2, f1, s2, s1):
                    df1_is_dominated[i] = True
                if dominates_stochastic(f1, f2, s1, s2):
                    df2_is_dominated[j] = True
        df1_dominated_by_df2    = df1[df1_is_dominated].reset_index(drop=True)
        df1_not_dominated_by_df2 = df1[[not x for x in df1_is_dominated]].reset_index(drop=True)
        df2_dominated_by_df1    = df2[df2_is_dominated].reset_index(drop=True)
        df2_not_dominated_by_df1 = df2[[not x for x in df2_is_dominated]].reset_index(drop=True)
        return (df1_dominated_by_df2, df1_not_dominated_by_df2, df2_dominated_by_df1, df2_not_dominated_by_df1)
    df1 = load_file(file_name1)
    df2 = load_file(file_name2)
    f1_dom_f2, f1_not_dom_f2, f2_dom_f1, f2_not_dom_f1 = classify(df1,df2)
    _, ax1 = plt.subplots(figsize=(10,5))
    ax1.scatter(f1_dom_f2['store_avg'], f1_dom_f2['retrieve_avg'], color="#009900", s=50, alpha=0.80, edgecolors='black', linewidth=0.5, marker='s',label=f'{label1}_dominated')
    ax1.scatter(f1_not_dom_f2['store_avg'], f1_not_dom_f2['retrieve_avg'], color="#FF6600", s=50, alpha=0.80, edgecolors='black', linewidth=0.5, marker='^',label=f'{label1}_non_dominated')
    ax1.scatter(f2_dom_f1['store_avg'], f2_dom_f1['retrieve_avg'], color="#BF00FF", s=50, alpha=0.80, edgecolors='black', linewidth=0.5, marker='o',label=f'{label2}_dominated')
    ax1.scatter(f2_not_dom_f1['store_avg'], f2_not_dom_f1['retrieve_avg'], color="#0000FF", s=50, alpha=0.80, edgecolors='black', linewidth=0.5, marker='D',label=f'{label2}_non_dominated')
    ax1.set_xlabel('Average storage flow time (s)', fontsize=15, fontweight='bold')
    ax1.set_ylabel('Average retrieval flow time (s)', fontsize=15, fontweight='bold')
    ax1.tick_params(axis='x', labelsize=12)
    ax1.tick_params(axis='y', labelsize=12)
    ax1.set_title(f'Average storage flow time x Average retrieval flow time - {subtitle}', fontsize=15, fontweight='bold')
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='best', fontsize=9, ncol=1)
    if xlim is not None: plt.xlim(xlim)
    if ylim is not None: plt.ylim(ylim)
    plt.tight_layout()

if __name__ == "__main__":
    xlim = None
    ylim = None
    # xlim = (0,100)
    # ylim = (0,100)

    plot_single_file("file_name.csv", "subtitle", xlim, ylim)
    plot_two_files("file_1_name.csv", "file_2_name.csv", "subtitle", xlim, ylim, "label_1", "label_2")
    plot_comparison("file_1_name.csv", "file_2_name.csv", "subtitle", xlim, ylim, "label_1", "label_2")

    plt.show()