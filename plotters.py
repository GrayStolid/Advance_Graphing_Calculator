"""
Plotting modules for different coordinate systems
"""

import math


class BasePlotter:
    """Base class for all plotters"""
    
    def __init__(self):
        self.parser = None
        try:
            from expression_parser import ExpressionParser
            self.parser = ExpressionParser()
        except ImportError:
            pass
    
    def safe_eval(self, expression, variables):
        """Safely evaluate expression with variables"""
        if self.parser:
            return self.parser.evaluate_expression(expression, variables)
        else:
            # Fallback evaluation
            expr = expression.replace('^', '**')
            for var, value in variables.items():
                expr = expr.replace(var, str(value))
            return eval(expr, {"__builtins__": {}, "math": math})


class Plotter2D(BasePlotter):
    """2D function plotter"""
    
    def plot(self, figure, expression, x_min=-10, x_max=10, num_points=500):
        """Plot 2D function"""
        try:
            import numpy as np
            
            figure.clear()
            ax = figure.add_subplot(111)
            
            # Generate x values
            x_values = np.linspace(x_min, x_max, num_points)
            y_values = []
            
            # Calculate y values
            for x in x_values:
                try:
                    y = self.safe_eval(expression, {'x': x})
                    y_values.append(y)
                except:
                    y_values.append(np.nan)
            
            # Plot
            ax.plot(x_values, y_values, 'b-', linewidth=2)
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('x')
            ax.set_ylabel('f(x)')
            ax.set_title(f'f(x) = {expression}')
            
            # Set reasonable y limits
            """valid_y = [y for y in y_values if not np.isnan(y) and not np.isinf(y)]
            if valid_y:
                y_min, y_max = min(valid_y), max(valid_y)
                y_range = y_max - y_min
                if y_range > 0:
                    ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)"""
            
            #figure.tight_layout()
            
        except Exception as e:
            # Create error plot
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error plotting 2D:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            ax.set_title('2D Plot Error')


class Plotter3D(BasePlotter):
    """3D surface plotter"""
    
    def plot(self, figure, expression, x_range=(-5, 5), y_range=(-5, 5), num_points=50):
        """Plot 3D surface"""
        try:
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            figure.clear()
            ax = figure.add_subplot(111, projection='3d')
            
            # Generate meshgrid
            x = np.linspace(x_range[0], x_range[1], num_points)
            y = np.linspace(y_range[0], y_range[1], num_points)
            X, Y = np.meshgrid(x, y)
            
            # Calculate Z values
            Z = np.zeros_like(X)
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    try:
                        Z[i, j] = self.safe_eval(expression, {'x': X[i, j], 'y': Y[i, j]})
                    except:
                        Z[i, j] = np.nan
            
            # Plot surface
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('f(x,y)')
            ax.set_title(f'f(x,y) = {expression}')
            
            # Add colorbar
            figure.colorbar(surf, ax=ax, shrink=0.5)
            
        except Exception as e:
            # Create error plot
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error plotting 3D:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            ax.set_title('3D Plot Error')


class PlotterPolar(BasePlotter):
    """Polar coordinate plotter"""
    
    def plot(self, figure, expression, theta_range=(0, 2*math.pi), num_points=1000):
        """Plot polar function"""
        try:
            import numpy as np
            
            figure.clear()
            ax = figure.add_subplot(111, projection='polar')
            
            # Generate theta values
            theta_values = np.linspace(theta_range[0], theta_range[1], num_points)
            r_values = []
            
            # Calculate r values
            for theta in theta_values:
                try:
                    r = self.safe_eval(expression, {'t': theta, 'theta': theta})
                    r_values.append(r)
                except:
                    r_values.append(np.nan)
            
            # Plot
            ax.plot(theta_values, r_values, 'b-', linewidth=2)
            ax.set_title(f'r(θ) = {expression}')
            ax.grid(True)
            
        except Exception as e:
            # Create error plot
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error plotting polar:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            ax.set_title('Polar Plot Error')


class PlotterSpherical(BasePlotter):
    """Spherical coordinate plotter"""
    
    def plot(self, figure, expression, theta_range=(0, math.pi), phi_range=(0, 2*math.pi), num_points=30):
        """Plot spherical function"""
        try:
            import numpy as np
            from mpl_toolkits.mplot3d import Axes3D
            
            figure.clear()
            ax = figure.add_subplot(111, projection='3d')
            
            # Generate spherical coordinates
            theta = np.linspace(theta_range[0], theta_range[1], num_points)
            phi = np.linspace(phi_range[0], phi_range[1], num_points)
            THETA, PHI = np.meshgrid(theta, phi)
            
            # Calculate r values
            R = np.zeros_like(THETA)
            for i in range(THETA.shape[0]):
                for j in range(THETA.shape[1]):
                    try:
                        R[i, j] = self.safe_eval(expression, {
                            'theta': THETA[i, j], 
                            'phi': PHI[i, j]
                        })
                    except:
                        R[i, j] = 1  # Default radius
            
            # Convert to Cartesian coordinates
            X = R * np.sin(THETA) * np.cos(PHI)
            Y = R * np.sin(THETA) * np.sin(PHI)
            Z = R * np.cos(THETA)
            
            # Plot surface
            surf = ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.8)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'r(θ,φ) = {expression}')
            
            # Make axes equal
            max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max() / 2.0
            mid_x = (X.max()+X.min()) * 0.5
            mid_y = (Y.max()+Y.min()) * 0.5
            mid_z = (Z.max()+Z.min()) * 0.5
            ax.set_xlim(mid_x - max_range, mid_x + max_range)
            ax.set_ylim(mid_y - max_range, mid_y + max_range)
            ax.set_zlim(mid_z - max_range, mid_z + max_range)
            
        except Exception as e:
            # Create error plot
            figure.clear()
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, f'Error plotting spherical:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            ax.set_title('Spherical Plot Error')
