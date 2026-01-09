from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time
import threading

def show_progress(task_name, percentage):
    """Simple function to return a progress bar string for compatibility"""
    bar_length = 28
    filled = int(bar_length * percentage / 100)
    bar = "█" * filled + " " * (bar_length - filled)
    return f"{task_name}... [{bar}] {percentage}%"

def show_rich_progress(task_name, total_steps=100):
    """Shows a rich progress bar that updates in real-time"""
    from rich.console import Console
    console = Console()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:

        task = progress.add_task(f"[cyan]{task_name}", total=total_steps)

        # Simulate progress for demonstration
        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(0.05)  # Adjust speed as needed
            if progress.tasks[0].completed >= total_steps:
                break

        return True

# Example usage
if __name__ == "__main__":
    print(show_progress("Analyzing codebase structure", 100))