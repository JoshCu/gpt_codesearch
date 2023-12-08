import subprocess
import os


def clone_repos(repo_list, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for repo in repo_list:
        repo_name = repo.split("/")[-1]
        clone_path = os.path.join(target_folder, repo_name)

        # Cloning the repository
        subprocess.run(["git", "clone", "--recurse-submodules", repo, clone_path])


# Example usage
repo_list = [
    "https://github.com/NOAA-OWP/ngen",
    "https://github.com/NOAA-OWP/t-route",
    "https://github.com/NOAA-OWP/hydrofabric",
    "https://github.com/NOAA-OWP/ngen-forcing",
    "https://github.com/NOAA-OWP/DMOD",
    "https://github.com/CUAHSI/domain-subsetter",
    "https://github.com/CUAHSI/metadata-extractor",
    "https://github.com/CUAHSI/notebooks",
    "https://github.com/NOAA-OWP/ngen-cal.git"
    # Add more repository URLs here
]
target_folder = "./repos"

clone_repos(repo_list, target_folder)
