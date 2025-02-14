# SecurePass Manager

SecurePass Manager is a secure, user-friendly password management application built with Python and PySide6. It provides encrypted storage for passwords along with features like password generation, categorization, and clipboard management.

## Features

- 🔒 Secure master password protection  
- 🔑 Strong encryption using Fernet (cryptography)  
- 📋 Automatic clipboard clearing  
- 🎯 Category-based password organization  
- 🔍 Quick search functionality  
- 🔄 Password generator  
- 📱 Minimizable to floating icon  
- 📤 Import/Export functionality  
- 🌙 Modern dark theme interface  

## Screenshots

![SecurePass Manager](https://sbist.com.np/securepass_manager/images/products/product4.png)

## Requirements

- Python 3.8+
- PySide6
- cryptography
- bcrypt

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thesantoshbist/SecurePass-Manager.git
   cd SecurePass-Manager
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **First Launch:**  
   - Set your master password when launching the app for the first time  
   - This password will be required for all future access  

2. **Managing Passwords:**  
   - Click '+' to add new passwords  
   - Use the search bar to find stored passwords  
   - Filter passwords by categories  
   - Click copy buttons to temporarily copy information to clipboard  

3. **Categories:**  
   - Organize passwords using custom categories  
   - Manage categories through the 'Manage Categories' button  

4. **Security Features:**  
   - Auto-clearing clipboard after copying sensitive information  
   - Encrypted storage of all passwords  
   - Session timeout for additional security  

## Security

- Passwords are encrypted using Fernet symmetric encryption
- Master password is hashed using bcrypt
- Clipboard contents are automatically cleared
- Database is encrypted with the master password

## Contributing

1. Fork the repository  
2. Create a new branch (`git checkout -b feature/improvement`)  
3. Commit your changes (`git commit -am 'Add new feature'`)  
4. Push to the branch (`git push origin feature/improvement`)  
5. Create a Pull Request  

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Santosh Bist**  
- Website: [sbist.com.np](https://sbist.com.np)

## Acknowledgments

- Built with PySide6 (Qt for Python)
- Icons from [Add icon source]
- Special thanks to contributors and testers

## Support

If you find this project helpful, please consider:
- Giving it a ⭐ on GitHub
- Reporting any issues you encounter
- Contributing to the project
- [Buying me a coffee ☕](https://ko-fi.com/santoshbist)

---

Made with ❤️ by **Santosh Bist**
