
<html>
<head>
</head>
<body>
<H1>FoCuS-point</H1>

<H4>Python TCSPC (Time Correlated Single Photon Counting) FCS (Fluorescence Correlation Spectroscopy)  data visualiser. </H4>

<p> The software for Windows and OSX is available through the following link and allows immediate access to FoCuS-point technique:
<p><a href ="http://sara.molbiol.ox.ac.uk/dwaithe/download_page.html#FoCuS">Click for downloads</a></p>
<p> For linux the software can be directly installed using pip. Using naive Ubuntu 14.04:</ol>
<ol> sudo apt-get install python-setuptools python-dev build-essential git-all libpng-dev libfreetype6-dev</ol>
<ol> sudo easy_install pip</ol>
<ol> sudo pip install —upgrade virtualenv numpy</ol>
<ol> sudo -H pip install git+https://github.com/dwaithe/FCS_point_correlator/ —upgrade</ol>
<ol> To run: python -m focuspoint.FCS_point_correlator</ol>
<p>Furthermore there is a technical manual which goes into the software in high detail.</p>
<p><a href ="http://sara.molbiol.ox.ac.uk/dwaithe/download_page.html#FoCuS-manual">Click for downloads</a></p>

<h3>FAQ</h3>
<p>Q: What datafiles does FoCuS-point support? A: Presently FoCuS-point supports '.pt3' uncorrelated files and in the fitting software FoCuS-point supports '.SIN' correlated files and '.csv' correlated files in FoCuS-point's own format.
<p>Q: I have data files which are not '.pt3' what can I do?  A: You can create an issue using github and I will make the software support your file format if possible. Furthermore you can write a parser which converts your file format to the FoCuS-point generic format which is comma delimited. More details can be found by following this link:<a href ="http://sara.molbiol.ox.ac.uk/dwaithe/download_page.html#FoCuS-generic"> Click for generic format</a></p>

</body>
</html>