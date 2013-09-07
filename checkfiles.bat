pushd "C:\Users\ALI\Desktop\textbookgen proj\crowdsource\experiment\elanpy\"
for %%F in ("E:\elan projects\L2\resubmission\*.eaf") do (
   python checkeaf.py -e "%%F"
)

pause