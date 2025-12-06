# 121_A3
Inverted index

Current uploaded code parses through DEV jsons and finds data by running through jsons locally.

To run the terminal, `python3 spacetime-crawler4py/launch.py --json_dir DEV --restart` to run launch over DEV directory of jsons. Note that line 53 of `launch.py` must be commented out in order to jump directly to query search, otherwise it will begin crawling and rebuilding the index.

In order to search using the web gui, run `python interface/web_interface.py`.

Change config.py fallback thread and delay to increase threads and decrease delay. default is 16 threads and 0.01 delay.
