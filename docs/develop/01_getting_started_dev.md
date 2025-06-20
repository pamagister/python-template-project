
# Getting started developing

## Setup your project development environment

Getting started on developing your own project based on this template

1. **Create** a new [github repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).
2. **Clone** [github repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the into your local file system.
    ```bash
    git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY
    ```
4. **Install** [uv package and project manager](https://docs.astral.sh/uv/getting-started/installation/)
    ```bash
    pip install uv
    ```
5. **Generate** [a sample project](https://docs.astral.sh/uv/guides/projects/#creating-a-new-project) with uv
6. Add and **push** the artifacts to your github repository
    ```bash
    git push
    ```
8. Copy the content of this repository into your repository

## Troubleshooting

### Problems with release pipeline

If you get this error below:
```bash
/home/runner/work/_temp/xxxx_xxx.sh: line 1: .github/release_message.sh: Permission denied
```

You have to run these commands in your IDE Terminal or the git bash and then push the changes.
```bash
git update-index --chmod=+x ./.github/release_message.sh
```

