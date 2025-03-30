# QuickCalc
# ![Icon](assets/icon.png)

QuickCalc is a lightweight and fast calculator application designed for personal use. It allows you to configure a hotkey that, when pressed, opens a window where you can quickly type text or basic math expressions (e.g., `2+2=`). The solution is automatically calculated and displayed at the bottom of the window. You can use the `Tab` key to autocomplete the solution, making calculations incredibly fast and efficient.

## Features
- **Hotkey Activation**: Configure a custom key to instantly open the calculator window.
- **Real-Time Calculation**: Automatically calculates the result of math expressions as you type.
- **Autocomplete**: Use the `Tab` key to quickly insert the calculated result.
- **Minimalist Design**: Built for speed and simplicity.

## Installation

### Option 1: Download the Executable
You can download the pre-built executable from the [Releases](https://github.com/Darkylt/QuickCalc/releases) tab.

_The trigger key in the pre-built version is `F18`._

### Option 2: Build It Yourself
1. Clone the repository:
   ```sh
   git clone https://github.com/Darkylt/QuickCalc.git
   cd QuickCalc
   ```
2. Create a virtual environment:
   ```sh
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source .venv/bin/activate
     ```
4. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
5. Configure your preferred hotkey in config.yml.
6. Run the build script:
   ```sh
   build.bat
   ```

## Configuration
Edit the config.yml file to set your preferred hotkey. For example:
```yaml
hotkey: F12
```
**Remember to configure prior to building!**

## Notes
- This program is tailored to my personal needs and system. Feature requests will not be accepted.
- Use at your own discretion.

## License
This project is licensed under the GNU General Public License v3.0. You can find the full license text in the [LICENSE](LICENSE) file.

For more details, visit [https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html).