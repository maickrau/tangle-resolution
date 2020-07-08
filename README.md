# Tangle resolution

Scripts used for resolving tangles in the T2T June 2020 workshop. The commands for running the tangle resolution are in commands.sh. Note that there are manual steps so you should run the commands by hand. Running commands.sh will not work.

### Installation

You need to have the following programs compiled and copied to the bin directory:

- [GraphAligner](https://github.com/maickrau/GraphAligner), tested with commit 856d30c927e
- [MBG](https://github.com/maickrau/MBG), tested with commit 8a2790566
- [gimbricate](https://github.com/ekg/gimbricate), tested with commit 212e16a2a1920
- [seqwish](https://github.com/ekg/seqwish), tested with commit 2bc49296a73c27d
- [vg](https://github.com/vgteam/vg), tested with v1.23.0

You also need the following programs in your path:

- [mummer4](https://github.com/mummer4/mummer), tested with bioconda version 4.0.0beta2

Also set permissions for the scripts:

- `chmod u+x scripts/*`
