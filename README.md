Here is the updated README file:

# mapping-make-my-trip

This repository contains a Python script for retrieving hotel price data from **MakeMyTrip**, a popular online travel booking platform.

### About MakeMyTrip
MakeMyTrip is one of India's leading online travel agencies, offering services such as hotel reservations, flight bookings, holiday packages, and more. It provides real-time pricing and availability for accommodations across various locations.

### Script Functionality
The script is designed to run periodically (3–4 times a day) and performs the following tasks:
- Fetches hotel prices for selected properties, specific room types, and a given location and date.
- Compares the retrieved prices against a predefined threshold.
- If the price falls below the threshold, the script sends an email notification to alert the user.

This automation helps users track price drops and book hotels at the best rates effortlessly.

### Deployment
The script is containerized using Docker and deployed on an AWS cloud instance, ensuring seamless execution and scalability. The Docker container provides a consistent and reliable environment for the script to run, allowing for easy maintenance and updates.

### Technical Details
- **Containerization**: Docker
- **Cloud Platform**: AWS
- **Programming Language**: Python
- **Schedule**: Periodic execution (3-4 times a day)

By leveraging Docker and AWS, the script can be easily scaled and managed, providing a robust and efficient solution for tracking hotel prices and sending notifications.
