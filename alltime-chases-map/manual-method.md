1. download summitslist.csv: https://storage.sota.org.uk/summitslist.csv
2. open summitslist.csv in libreoffice calc (excel), save as proper spreadsheet file (.ods or .xlsx)
3. go to your chaser uniques page: https://www.sotadata.org.uk/en/logs/uniques/chaser/
4. highlight the whole table with your mouse, Ctrl-C to copy
5. in calc, create a new sheet within the same summitslist.csv spreadsheet
6. in row 2 of new sheet, Ctrl-Shift-V, paste "Unformatted text". In the next dialog box, choose Tab and Other as delimiters, enter "()" in the textbox next to Other
7. insert new column
8. title the columns (starting in A1 and working right) "Order", "SummitCode", "Name", "Lat", "Long", "ChaseCount", "FirstChaseDate"
9. I3, `=COUNTA(summitslist.A:summitslist.A)` (to get the # of rows, which changes over time as summits are added/removed)
10. J3, `="summitslist.A$" & I3`, text concatenation to get a reference to the last cell in the SummitCode (A) column
11. K3, `="summitslist.H$" & I3`, text concatenation to get a reference to the last cell in the GridRef2 (H) column
12. L3, `="summitslist.I$" & I3`, text concatenation to get a reference to the last cell in the Latitude (I) column
13. D2, `=LOOKUP($B2, summitslist.$A$3:INDIRECT($J$3), summitslist.H$3:INDIRECT(K$3))`. after entry, it should turn into the latitude of the summit in that row
14. corner-drag D2 into E2 to copy the formula over. it should turn into the longitude of the summit in that row
15. corner drag the 2-cell (D2 and E2) selection down until the last row of your unique summits
16. save the spreadsheet document
17. File -> Save a Copy, from the filetype dropdown select "Text CSV (.csv)", pick a filename, save. keep the default settings in the "Export Text File" dialog. you might get a warning saying "Only the active sheet was saved", which is okay because that's exactly what we want
18. https://www.google.com/maps/d/?hl=en, "Create a New Map"
19. under "Untitled layer", select "Import". in the "Upload" tab of the dialog select "Browse", then select the .csv file just exported
20. select latitude and longitude columns
21. choose a column to use as titles, I usually pick either Name or SummitCode
22. once imported, the layer will be named the filename. underneath the layer name it will say "Uniform style". click here and you can pick different styles for the summit markers. I like to pick the Name row under "Set labels" and the ChaseCount row under "Group places by", then pick "Ranges" instead of "Categories" and select a # of bins and color scheme that makes sense to me
