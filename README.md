# Python_Project_Sample
An API test infrastructure built for test engineering application.  Includes test &amp; test-creation programs, testcases &amp; documentation

This is a sample of my python coding, test infrastructure design and documentation writing primarily placed here for inspection by potential employers.  I originally wrote it in November 2016 as a sample python software API testing project for evaluation by a Boulder-based company.  Almost all of my previous C++, python & script work is owned by my former employer Xilinx and was never open-sourced. I decided to add this project to my GitHub repository to keep for future reference by any other potential employers.

The purpose of this project is to thoroughly test a sample web JSON-RPC API method for playing online chess.  I've chosen not to upload the original assignment/requirements document since that is the property of the company interviewing me. I only submitted it the day before I did this GitHub commit, so no feedback yet on what they think.

All documents and files in this repository were written solely by me, and I reserve any authorship claims and copyrights.  They are however open for inspection and evaluation as well as critical feedback if appropriate.

DOCUMENTATION:  See the included SolidFire_Chess_Service_Test_Strategy.docx word document, as well as the project README below.

DOWNLOAD & RUN: dan_doran_SFCS_sssignment.tar.gz   - See 'QUICK START' section at bottom of this page.

Below is a copy of the contained README File:
========================================================================
SolidFire Chess Service Testing and Test Case Creation Program
(A SolidFire/NetApp employment interviewee Software Assignment)

Copyright 2016,  Dan Doran, Electronic & Software Engineer, Boulder CO.
Contact:  dancdoran@gmail.com , 303-709-6746
Date:  11/16/2016

'QUICK START' INSTRUCTIONS AT BOTTOM (for you impatient types)

This testing/case creation suite is specifiaclly designed to test the
SolidFire Chess Service API 'MakeMove' method that validates boards &
moves submitted by online chess players.

SUPPORTED PLATFORMS:  Windows terminal & Ubuntu Linux v14.04 shell.

SOFTWARE REQUIREMENTS:  Windows or Ubuntu Linux v14.04,  python v3.1 or
                        newer, "requests" python module for python3.

INSTALLING "requests" PYTHON MODULE: >: pip3.4 install requests

CONTENTS:
1) RequestGen.py - A python3 script to interactively create a new functional
   or expected error test case definition file.  Runs in created test directory.
   Usage:  python RequestGen.py

2) Run_SFCS_Tests.py - A python3 script to run some or all of the test case
   repository cases, creating a Test_Report_<date>_<time>.report summary file
   and a Test_API_<date>_<time>.log file cotaining all requests & responses.
   Usage: python Run_SFCS_Tests.py [-l Path_to_list_of_testcase_files] [-s Path_to_single_test_file]
          Path_to_list_of_testcase_files: optional ascii file with one testcase path on each line
          Path_to_single_test_file: optional single test case definition file path
          (Default is to run all tests in the test case directories.)

3) utilities.py - A python3 module containing shared functions used by both programs.
                  Not executeable.

4) 'Test_Boards' Directory - A repository for starting chess boardStates
   (python Lists in ascii form). Facilitates rapid new test case development
   by allowing developers to re-use exisiting boards.  There are 5 subdirs/categories
   for various test board setup types. All boards have .bsfile file extensions:
     1) Start_Game
     2) Invalid_Boards
     3) Piece_Moves
     4) Piece_Captures
     5) End_Game

5) 'expPassTestDir' Directory - A repository directory for functional test case definition
   files.  These tests are expected to generate a full API response which is checked
   for expected results by the Run_SFCS_Tests.py tet script.  Any Failures reported from
   this directory of tests should be investigated as potential SFCS API bugs. All case
   definition files have '.passtest' file extensions.

6) 'expFailTestDir' Directory - A repository directory for expected error test definition
   files.  These tests are expected to return a designated response API Error Code which is
   is checked by the Run_SFCS_Tests.py script.  Any Failures reported here indicate an
   unexpected response or error code was received in the response API and should be
   investigated as a potential SFCS API bug. All files have '.expfail' file extensions.

7) linux_testcase_list and win_testcase_list - sample lists of testcase paths that can be
   used with the 'Run_SFCS_Tests -l' option to run a designated subset of all test cases.

QUICK START:

   To run all existing tests:
   >: python Run_SFCS_Tests.py
   Test results streamed to screen and the test .report and .log files.

   To quickly create a new test case:
   >: python RequestGen.py
   Allows you to interactively generate a test chess board & move using pre-made
   starting boards or generate a new starting board.  Once the test case is
   successfully generated, it can be tested as follows:
   >: python Run_SFCS_Tests.py -s <path_to/new_testcase>
