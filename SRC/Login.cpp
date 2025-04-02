#include <iostream>
#include <string>

using namespace std;

// Function to validate the password
bool validatePassword(const string& input) {
    const string correct_password = "secure123";
    return input == correct_password;
}

// Function to display login message
void displayMessage(bool isSuccess) {
    if (isSuccess) {
        cout << "\nLogin successful! Welcome to the Expense Tracker.\n";
        cout << "You can now access all features.\n";
    } else {
        cout << "\nIncorrect password! Please try again.\n";
    }
}

int main() {
    string password;
    const int max_attempts = 3;
    int attempts = 0;

    cout << "==== Expense Tracker Login ====\n";

    while (attempts < max_attempts) {
        cout << "Enter password: ";
        cin >> password;

        if (validatePassword(password)) {
            displayMessage(true);
            return 0;
        } else {
            displayMessage(false);
            attempts++;
        }

        if (attempts == max_attempts) {
            cout << "Too many failed attempts. Access denied.\n";
        }
    }

    return 1;
}
