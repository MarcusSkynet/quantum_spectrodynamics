#!/usr/bin/env python3
"""
QSD Interactive Animated Visualizations
========================================

Creates animated visualizations of QSD mechanisms.

Author: M. Hubka
Date: February 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle
import matplotlib.colors as mcolors
import os

# QSD Constants
PHI = (1 + np.sqrt(5)) / 2
Hb4 = 1 / (4 * np.log(2))
DELTA = 3 / (80 * PHI**2)


class K4C5Animation:
    """Animate Kâ‚„ âˆª Câ‚… structure dynamics."""
    
    def __init__(self, figsize=(12, 6)):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=figsize)
        self.fig.suptitle('QSD Fundamental Structures: Kâ‚„ âˆª Câ‚… Dynamics', fontsize=14)
        
        theta = np.array([0, 2*np.pi/3, 4*np.pi/3])
        self.k4_nodes = {
            0: np.array([0, 0]),
            1: np.array([np.cos(theta[0]), np.sin(theta[0])]),
            2: np.array([np.cos(theta[1]), np.sin(theta[1])]),
            3: np.array([np.cos(theta[2]), np.sin(theta[2])])
        }
        self.k4_edges = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        
        theta_c5 = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, 5, endpoint=False)
        self.c5_nodes = [np.array([np.cos(t), np.sin(t)]) for t in theta_c5]
        
    def init_plots(self):
        for ax in [self.ax1, self.ax2]:
            ax.clear()
            ax.set_xlim(-1.8, 1.8)
            ax.set_ylim(-1.8, 1.8)
            ax.set_aspect('equal')
            ax.axis('off')
        
        self.ax1.set_title('Kâ‚„: Complete Graph', fontsize=12)
        self.ax2.set_title('Câ‚…: Pentagon', fontsize=12)
        
        # Kâ‚„ edges
        for i, j in self.k4_edges:
            x = [self.k4_nodes[i][0], self.k4_nodes[j][0]]
            y = [self.k4_nodes[i][1], self.k4_nodes[j][1]]
            self.ax1.plot(x, y, 'b-', linewidth=2, alpha=0.5)
        
        # Kâ‚„ nodes
        self.k4_circles = []
        colors = ['red', 'blue', 'blue', 'blue']
        labels = ['W', 'X', 'Y', 'Z']
        for pos, color, label in zip(self.k4_nodes.values(), colors, labels):
            circle = Circle(pos, 0.15, facecolor=color, edgecolor='black', linewidth=2)
            self.ax1.add_patch(circle)
            self.k4_circles.append(circle)
            self.ax1.text(pos[0], pos[1], label, ha='center', va='center',
                        fontsize=12, color='white', fontweight='bold', zorder=4)
        
        # Câ‚… edges
        for i in range(5):
            j = (i + 1) % 5
            x = [self.c5_nodes[i][0], self.c5_nodes[j][0]]
            y = [self.c5_nodes[i][1], self.c5_nodes[j][1]]
            self.ax2.plot(x, y, 'g-', linewidth=2)
        
        # Câ‚… diagonals
        for i in range(5):
            j = (i + 2) % 5
            x = [self.c5_nodes[i][0], self.c5_nodes[j][0]]
            y = [self.c5_nodes[i][1], self.c5_nodes[j][1]]
            self.ax2.plot(x, y, 'g--', linewidth=1, alpha=0.3)
        
        # Câ‚… nodes
        self.c5_circles = []
        for i, pos in enumerate(self.c5_nodes):
            circle = Circle(pos, 0.12, facecolor='green', edgecolor='black', linewidth=2)
            self.ax2.add_patch(circle)
            self.c5_circles.append(circle)
            self.ax2.text(pos[0], pos[1], str(i+1), ha='center', va='center',
                        fontsize=10, color='white', fontweight='bold', zorder=4)
        
        self.phi_text = self.ax2.text(0, -1.5, '', ha='center', fontsize=10,
                                      bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        return self.k4_circles + self.c5_circles
    
    def animate(self, frame):
        t = frame / 60
        
        # Pulse anchor
        pulse = 0.15 + 0.03 * np.sin(2 * np.pi * t * 3)
        self.k4_circles[0].set_radius(pulse)
        
        # Oscillate Câ‚… nodes
        for i, circle in enumerate(self.c5_circles):
            base_pos = self.c5_nodes[i]
            oscillation = 0.02 * np.sin(2 * np.pi * t * 2 + i * 2 * np.pi / 5)
            circle.center = base_pos * (1 + oscillation)
        
        self.phi_text.set_text(f'Î»â‚‚/Î»â‚ = Ï†Â² = {PHI**2:.4f}')
        
        return self.k4_circles + self.c5_circles + [self.phi_text]
    
    def create_animation(self, frames=60, interval=50, save_path=None):
        self.init_plots()
        anim = FuncAnimation(self.fig, self.animate, frames=frames,
                            interval=interval, blit=False, init_func=self.init_plots)
        if save_path:
            writer = PillowWriter(fps=20)
            anim.save(save_path, writer=writer)
            print(f"Saved: {save_path}")
        plt.close()
        return anim


class ErrorCorrectionAnimation:
    """Animate [[5,1,3]] error correction."""
    
    def __init__(self, figsize=(10, 8)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.suptitle('[[5,1,3]] Quantum Error Correction', fontsize=14)
        
        theta = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, 5, endpoint=False)
        self.qubit_positions = [np.array([np.cos(t), np.sin(t)]) for t in theta]
        
    def init_plot(self):
        self.ax.clear()
        self.ax.set_xlim(-2, 2)
        self.ax.set_ylim(-2.2, 2)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        for i in range(5):
            for j in range(i+1, 5):
                p1, p2 = self.qubit_positions[i], self.qubit_positions[j]
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'gray', linewidth=1, alpha=0.3)
        
        self.qubit_circles = []
        self.qubit_texts = []
        
        for i, pos in enumerate(self.qubit_positions):
            circle = Circle(pos, 0.18, facecolor='lightblue', edgecolor='black', linewidth=2)
            self.ax.add_patch(circle)
            self.qubit_circles.append(circle)
            text = self.ax.text(pos[0], pos[1], f'q{i+1}\n|0âŸ©', ha='center', va='center', fontsize=9)
            self.qubit_texts.append(text)
        
        self.status_text = self.ax.text(0, -1.7, '', ha='center', fontsize=12,
                                        bbox=dict(boxstyle='round', facecolor='white'))
        self.syndrome_text = self.ax.text(0, 1.7, '', ha='center', fontsize=11,
                                          bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        return self.qubit_circles + self.qubit_texts
    
    def animate(self, frame):
        phase = frame % 80
        
        if phase < 20:
            self.status_text.set_text('Logical qubit encoded: |ÏˆâŸ©_L')
            self.syndrome_text.set_text('Syndrome: (0,0,0,0) - No error')
            for i, circle in enumerate(self.qubit_circles):
                circle.set_facecolor('lightblue')
                self.qubit_texts[i].set_text(f'q{i+1}\n|0âŸ©')
                
        elif phase < 35:
            self.status_text.set_text('âš  X-error on qubit 3!')
            self.syndrome_text.set_text('Syndrome: measuring...')
            self.qubit_circles[2].set_facecolor('red')
            self.qubit_texts[2].set_text('q3\n|1âŸ©')
            
        elif phase < 55:
            self.status_text.set_text('Syndrome measurement complete')
            self.syndrome_text.set_text('Syndrome: (0,1,1,0) â†’ Error on q3')
            
        elif phase < 70:
            correction_progress = (phase - 55) / 15
            self.status_text.set_text('Applying X correction to qubit 3...')
            color = mcolors.to_rgba('red', alpha=1 - correction_progress)
            self.qubit_circles[2].set_facecolor(color)
            if correction_progress > 0.5:
                self.qubit_texts[2].set_text('q3\n|0âŸ©')
        else:
            self.status_text.set_text('âœ“ Error corrected! Logical qubit preserved.')
            self.syndrome_text.set_text('Syndrome: (0,0,0,0) - No error')
            for i, circle in enumerate(self.qubit_circles):
                circle.set_facecolor('lightgreen')
        
        return self.qubit_circles + self.qubit_texts + [self.status_text, self.syndrome_text]
    
    def create_animation(self, frames=160, interval=50, save_path=None):
        self.init_plot()
        anim = FuncAnimation(self.fig, self.animate, frames=frames,
                            interval=interval, blit=False, init_func=self.init_plot)
        if save_path:
            writer = PillowWriter(fps=20)
            anim.save(save_path, writer=writer)
            print(f"Saved: {save_path}")
        plt.close()
        return anim


class RenormalizationFlowAnimation:
    """Animate 3-loop renormalization flow."""
    
    def __init__(self, figsize=(10, 6)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.suptitle('QSD 3-Loop Renormalization Flow', fontsize=14)
        
        self.stages = ['Tree', '1-loop', '2-loop', '3-loop']
        self.values = [136.826, 137.065, 137.043, 137.036]
        self.corrections = [0, +0.239, -0.022, -0.007]
        self.exp_value = 137.035999
        
    def init_plot(self):
        self.ax.clear()
        self.ax.set_xlim(-0.5, 4)
        self.ax.set_ylim(136.5, 137.2)
        self.ax.set_xlabel('Loop Order', fontsize=12)
        self.ax.set_ylabel('Î±â»Â¹', fontsize=12)
        
        self.ax.axhline(y=self.exp_value, color='red', linestyle='--',
                       linewidth=2, label=f'Experiment: {self.exp_value}')
        
        self.bars = self.ax.bar(range(4), [0]*4, color='steelblue', alpha=0.7,
                               edgecolor='black', linewidth=2)
        
        self.value_texts = [self.ax.text(i, 136.6, '', ha='center', fontsize=10) for i in range(4)]
        self.corr_texts = [self.ax.text(i, 136.55, '', ha='center', fontsize=9) for i in range(4)]
        
        self.ax.set_xticks(range(4))
        self.ax.set_xticklabels(self.stages)
        self.ax.legend(loc='lower right')
        
        self.status = self.ax.text(2, 137.15, '', ha='center', fontsize=11,
                                   bbox=dict(boxstyle='round', facecolor='lightyellow'))
        
        return list(self.bars)
    
    def animate(self, frame):
        frames_per_stage = 30
        current_stage = min(frame // frames_per_stage, 3)
        stage_progress = min((frame % frames_per_stage) / frames_per_stage, 1)
        
        for i in range(4):
            if i < current_stage:
                self.bars[i].set_height(self.values[i] - 136.5)
                self.value_texts[i].set_text(f'{self.values[i]:.3f}')
                self.value_texts[i].set_position((i, self.values[i] + 0.02))
                if self.corrections[i] != 0:
                    sign = '+' if self.corrections[i] > 0 else ''
                    self.corr_texts[i].set_text(f'({sign}{self.corrections[i]:.3f})')
                    self.corr_texts[i].set_position((i, self.values[i] - 0.05))
                    self.corr_texts[i].set_color('green' if self.corrections[i] > 0 else 'red')
            elif i == current_stage:
                prev = self.values[i-1] if i > 0 else 136.5
                target = self.values[i]
                current = prev + stage_progress * (target - prev)
                self.bars[i].set_height(current - 136.5)
                self.value_texts[i].set_text(f'{current:.3f}')
                self.value_texts[i].set_position((i, current + 0.02))
            else:
                self.bars[i].set_height(0)
                self.value_texts[i].set_text('')
                self.corr_texts[i].set_text('')
        
        descriptions = [
            'Tree level: Gauge unification',
            '1-loop: Network friction (+0.239)',
            '2-loop: Radion feedback (-0.022)',
            '3-loop: Vacuum drag (-0.007)\nSeries TERMINATES!'
        ]
        self.status.set_text(descriptions[current_stage])
        
        return list(self.bars) + self.value_texts + self.corr_texts + [self.status]
    
    def create_animation(self, frames=120, interval=50, save_path=None):
        self.init_plot()
        anim = FuncAnimation(self.fig, self.animate, frames=frames,
                            interval=interval, blit=False, init_func=self.init_plot)
        if save_path:
            writer = PillowWriter(fps=20)
            anim.save(save_path, writer=writer)
            print(f"Saved: {save_path}")
        plt.close()
        return anim


class EnergyScaleCascade:
    """Animate energy scale cascade."""
    
    def __init__(self, figsize=(12, 8)):
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.fig.suptitle('QSD Energy Scale Cascade', fontsize=14)
        
        self.scales = [
            ('M_Planck', 1.22e19, 'darkred'),
            ('M_Pl/2^60', 10.59, 'red'),
            ('Î¼â‚€', 25.34, 'blue'),
            ('E_syn', 28.24, 'purple'),
            ('m_H', 126.71, 'green'),
        ]
        
    def init_plot(self):
        self.ax.clear()
        self.ax.set_xlim(-0.5, 22)
        self.ax.set_ylim(-0.5, 5)
        self.ax.set_xlabel('logâ‚â‚€(Energy / GeV)', fontsize=12)
        
        names = [s[0] for s in self.scales]
        self.bars = self.ax.barh(range(len(self.scales)), [0]*len(self.scales),
                                 color=[s[2] for s in self.scales], alpha=0.7)
        
        self.ax.set_yticks(range(len(self.scales)))
        self.ax.set_yticklabels(names)
        
        self.labels = [self.ax.text(0.5, i, '', va='center', fontsize=10) for i in range(len(self.scales))]
        
        return list(self.bars)
    
    def animate(self, frame):
        for i, (name, energy, color) in enumerate(self.scales):
            start_frame = i * 15
            if frame >= start_frame:
                progress = min((frame - start_frame) / 20, 1)
                log_energy = np.log10(energy)
                current_log = progress * log_energy
                self.bars[i].set_width(current_log)
                self.labels[i].set_text(f'{energy:.2e} GeV')
                self.labels[i].set_position((current_log + 0.3, i))
            else:
                self.bars[i].set_width(0)
                self.labels[i].set_text('')
        
        return list(self.bars) + self.labels
    
    def create_animation(self, frames=100, interval=50, save_path=None):
        self.init_plot()
        anim = FuncAnimation(self.fig, self.animate, frames=frames,
                            interval=interval, blit=False, init_func=self.init_plot)
        if save_path:
            writer = PillowWriter(fps=20)
            anim.save(save_path, writer=writer)
            print(f"Saved: {save_path}")
        plt.close()
        return anim


def generate_all_animations(output_dir='figures'):
    """Generate all QSD animations."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating QSD animations...")
    
    print("\n1. Kâ‚„ âˆª Câ‚… structure dynamics...")
    k4c5 = K4C5Animation()
    k4c5.create_animation(frames=60, save_path=os.path.join(output_dir, 'k4_c5_animation.gif'))
    
    print("2. [[5,1,3]] error correction...")
    error = ErrorCorrectionAnimation()
    error.create_animation(frames=160, save_path=os.path.join(output_dir, 'error_correction.gif'))
    
    print("3. Renormalization flow...")
    renorm = RenormalizationFlowAnimation()
    renorm.create_animation(frames=120, save_path=os.path.join(output_dir, 'renormalization_flow.gif'))
    
    print("4. Energy scale cascade...")
    cascade = EnergyScaleCascade()
    cascade.create_animation(frames=100, save_path=os.path.join(output_dir, 'energy_cascade.gif'))
    
    print(f"\nAll animations saved to: {output_dir}/")


if __name__ == "__main__":
    generate_all_animations()
