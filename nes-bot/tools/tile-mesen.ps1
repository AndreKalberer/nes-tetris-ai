# Tile every live-watch Mesen window (the mesence-live<i> copies) in a grid on the main screen.
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System; using System.Runtime.InteropServices;
public class W { [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int ht,bool r);
                 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c); }
'@
$wins = Get-Process Mesen -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*mesence-live*' -and $_.MainWindowHandle -ne 0 } |
        Sort-Object { $_.Path }
$n = @($wins).Count
if ($n -eq 0) { Write-Host 'No live-watch Mesen windows found'; exit }
$area = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$cols = [math]::Ceiling([math]::Sqrt($n)); $rows = [math]::Ceiling($n / $cols)
$w = [int]($area.Width / $cols); $h = [int]($area.Height / $rows)
$i = 0
foreach ($p in $wins) {
  [W]::ShowWindow($p.MainWindowHandle, 9) | Out-Null   # restore if maximised/minimised
  [W]::MoveWindow($p.MainWindowHandle, $area.X + ($i % $cols) * $w, $area.Y + [math]::Floor($i / $cols) * $h, $w, $h, $true) | Out-Null
  $i++
}
Write-Host "Tiled $n Mesen windows ($cols x $rows)"
