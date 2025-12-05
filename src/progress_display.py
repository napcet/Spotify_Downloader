"""
Enhanced Progress Display using Rich
Beautiful terminal output with progress bars and live updates.
"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from typing import Optional
import time


class ProgressDisplay:
    """Enhanced progress display using Rich library."""
    
    def __init__(self, total_tracks: int = 0):
        self.console = Console()
        self.start_time = time.time()
        self.total_tracks = total_tracks
        self.completed = 0
        self.failed = 0
        self.skipped = 0
        self.failed_tracks = []
        
        # Create progress bar
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            console=self.console
        )
        
        self.main_task = None
        
    def print_header(self):
        """Print a beautiful header."""
        self.console.print()
        self.console.print(Panel.fit(
            "[bold cyan]🎵  SPOTIFY MUSIC DOWNLOADER[/bold cyan]",
            border_style="cyan"
        ))
        self.console.print()
    
    def print_source_info(self, sources: list):
        """Print available download sources."""
        source_icons = {
            'internetarchive': '📚',
            'jamendo': '🎹',
            'deezer': '🎼',
            'youtube': '📺',
            'soundcloud': '☁️',
            'bandcamp': '🎸'
        }
        
        source_labels = {
            'internetarchive': 'INTERNET ARCHIVE (FREE FLAC)',
            'jamendo': 'JAMENDO (FREE CC)',
            'deezer': 'DEEZER',
            'youtube': 'YOUTUBE',
            'soundcloud': 'SOUNDCLOUD',
            'bandcamp': 'BANDCAMP'
        }
        
        table = Table(title="📡 Available Sources", show_header=False, box=None)
        
        for i, source in enumerate(sources):
            icon = source_icons.get(source, '🔊')
            label = source_labels.get(source, source.upper())
            status = "[green]✓ PRIMARY[/green]" if i == 0 else "[blue]✓ FALLBACK[/blue]"
            table.add_row(f"{icon}  {label}", status)
        
        self.console.print(table)
        self.console.print()
    
    def start_progress(self):
        """Start the progress bar."""
        self.progress.start()
        self.main_task = self.progress.add_task(
            "[cyan]Downloading tracks...",
            total=self.total_tracks
        )
    
    def stop_progress(self):
        """Stop the progress bar."""
        if self.progress:
            self.progress.stop()
    
    def print_track_info(self, track_num: int, total: int, track: dict):
        """Print current track being processed."""
        artist = track['artist'][:40]
        title = track['name'][:50]
        
        # Update progress description with stats
        stats = f"│ [green]✓ {self.completed}[/green] │ [red]✗ {self.failed}[/red] │ [yellow]⊙ {self.skipped}[/yellow]"
        
        # Update progress description
        if self.main_task is not None:
            self.progress.update(
                self.main_task,
                description=f"[cyan]🎵 {artist} - {title} {stats}"
            )
    
    def print_download_progress(self, source: str, percent: float, speed: str, eta: str):
        """Print download progress bar (legacy compatibility - not used with Rich)."""
        pass
    
    def print_success(self, track_name: str, file_size: float, source: str):
        """Print success message."""
        self.completed += 1
        
        source_icons = {
            'internetarchive': '📚',
            'jamendo': '🎹',
            'deezer': '🎼',
            'youtube': '📺'
        }
        icon = source_icons.get(source, '🔊')
        
        # Log above progress bar
        self.console.print(f"{icon} [green]✓[/green] {track_name[:60]} [dim][{file_size:.1f}MB][/dim]")
        
        # Update progress
        if self.main_task is not None:
            self.progress.update(
                self.main_task,
                advance=1
            )
    
    def print_skip(self, track_name: str, file_size: float):
        """Print skip message."""
        self.skipped += 1
        
        self.console.print(f"[yellow]⊙[/yellow] {track_name[:60]} [dim](exists)[/dim]")
        
        if self.main_task is not None:
            self.progress.update(
                self.main_task,
                advance=1
            )
    
    def print_error(self, track_name: str, error: str, track_info: dict = None):
        """Print error message."""
        self.failed += 1
        
        # Store detailed info for retry functionality
        if track_info:
            self.failed_tracks.append({
                'name': track_info.get('name'),
                'artist': track_info.get('artist'),
                'url': track_info.get('spotify_url')
            })
        else:
            self.failed_tracks.append({'name': track_name})
        
        self.console.print(f"[red]✗[/red] {track_name[:60]} [dim](failed)[/dim]")
        
        if self.main_task is not None:
            self.progress.update(
                self.main_task,
                advance=1
            )
    
    def print_retry(self, attempt: int, max_attempts: int, source: str):
        """Print retry message."""
        self.console.print(f"   [yellow]⟳ Retry {attempt}/{max_attempts} via {source.upper()}...[/yellow]")
    
    def print_summary(self, elapsed: float):
        """Print final summary."""
        self.console.print()
        
        total = self.completed + self.failed + self.skipped
        success_rate = (self.completed / total * 100) if total > 0 else 0
        
        # Create summary table
        summary_table = Table(title="📊 DOWNLOAD SUMMARY", show_header=False, box=None)
        summary_table.add_row("[green]✓ Completed:[/green]", f"{self.completed:3d}")
        summary_table.add_row("[red]✗ Failed:[/red]", f"{self.failed:3d}")
        summary_table.add_row("[yellow]⊙ Skipped:[/yellow]", f"{self.skipped:3d}")
        summary_table.add_row("━━━━━━━━━━━━━━━━━", "")
        summary_table.add_row("[bold]∑ Total:[/bold]", f"{total:3d}")
        summary_table.add_row("", "")
        summary_table.add_row("[bold]Success Rate:[/bold]", f"{success_rate:.1f}%")
        summary_table.add_row("[bold]Time Elapsed:[/bold]", self._format_time(elapsed))
        
        if self.completed > 0:
            avg_time = elapsed / self.completed
            summary_table.add_row("[bold]Avg per song:[/bold]", f"{avg_time:.1f}s")
        
        self.console.print(Panel(summary_table, border_style="cyan"))
        
        # Show failed tracks if any
        if self.failed > 0 and self.failed_tracks:
            self.console.print()
            self.console.print(f"[red]❌ Failed Downloads ({self.failed}):[/red]")
            self.console.rule(style="red")
            for i, track in enumerate(self.failed_tracks, 1):
                self.console.print(f"  {i:2d}. {track}")
            self.console.print()
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to human-readable time."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            mins = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{mins}m {secs}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"
