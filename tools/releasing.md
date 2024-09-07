
# Releasing tbp

- On a branch do the following.
  - Update the version numbers in `./src/tbp/__init__.py` and `./docs/data/version.yml`.
  - Update ./CHANGELOG.md with changes if not already in the UNRELEASED section.
- Create PR with above changes.
- Merge into main.
- Verify all build, linting, testing, and website deployment work.
- Create a new tag on the main branch with the format `#.#.#` AKA SemVer.
- Create a new release on GitHub copying over the relevant changes.
- Make sure the new release has the _latest_ mark.
