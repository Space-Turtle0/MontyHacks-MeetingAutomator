# MontyHacks-ZoomAutomator
 
ZoomAutomator by Rohit

I'll quickly go over what this does and how it works.

First off the program uses a SQLite Database in order to store information
and it uses a library called PyInquirer to display the Command Line Interface.

ZoomAutomator is supposed to be a program that allows you to join meetings automatically
without having to manually open the link. This helps prevent you from being tardy
from any time sensitive meetings. There are 2 major functions that power the program,
the CLI and the backgroundTask. The backgroundTask is responsible for querying the current
time in the database and opening any associated meetings while the CLI is responsible
for providing the user interface and actually allowing the user (you) to manage the database.
