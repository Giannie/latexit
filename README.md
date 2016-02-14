# latexit

A web server to serve up latex images to Slack. This requires a working installation of texlive in order to function. A full installation can be achieved by running:

    sudo apt-get install texlive-full imagemagick

For a more minimal installation that has all required components:

    sudo apt-get install texlive-base tex-common texlive-extra-utils xzdec imagemagick

If you use this minimal installation, the standalone latex package will need to be installed via:

    tlmgr init-usertree && tlmgr install standalone

In addition to this, some python packages are required as included in the requirements.txt file. Install via:

    sudo pip install -r requirements.txt
