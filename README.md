OSU-Course-Registration
=======================

Please check out the license file in this project.

This project has multiple pieces to it.

### Course Scraper

This portion of the project is meant to be used for collecting all of the course information for Oregon State University classes so a person can make an informed decision and plan out their next term(s) at Oregon State University well in advance. This repository will eventually be combined with another for automated planning out of the courses the user should take in the most efficient manner (where the cost is amount of quarters spent in school).

### Course Registration
Given a list of CRNs, this will attempt to register every class given at the time it is ran. It is recommended to run this via a cron job to ensure it is ran at the correct time.

#### Usage
If you already have your pin number use the following template.

```python register.py -u username -p password -n pin_number```

```username``` is your PIN (or the username of your ONID email like so: username@onid.orst.edu)

```password``` is your GAP or your ONID password

```pin_number``` is your pin number given to you for registration by your adviser


If you do not have your pin number yet use the following template.

```python register.py -u username -p password --bruteforce```

```username``` is your PIN (or the username of your ONID email like so: username@onid.orst.edu)

```password``` is your GAP or your ONID password

```--bruteforce``` means that the program will try every possible pin from 000000 to 999999. This will take a _very_ long time!
