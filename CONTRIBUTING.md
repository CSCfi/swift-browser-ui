## How to contribute

If you're reading this, it means you saw something that is not right, you want to add a new feature or your manager asked you to contribute to this. In any case we are glad and it would be awesome if you can contribute.

### Testing

We have a handful of unit tests. In our Git workflow unit tests are run on every Push and Pull Request.


### Submitting Issues

We have templates for submitting new issues, that you can fill out. For example if you found a bug, use the Bug Report template

### Submitting changes

When you made some changes you are happy with please send a [GitHub Pull Request to swift-x-account-sharing](https://github.com/CSCfi/swift-x-account-sharing/pull_requests/new/master) with a clear list of what you've done (read more about [pull requests]https://help.github.com/en/articles/about-pull-requests)). When you create that Merge Request, we will forever be in your debt if you check previous docs for typos.

Please follow our Git branches model and coding conventions (both below), and make sure all of your commits are atomic (preferably one feature per commit) and it is recommended a Merge Request addresses one functionality or fixes one bug.

Always write a clear log message for your commits, and if there is an issue open, reference that issue. This guide might help: [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/).

Once submitted, the Merge Request will go through a review process, meaning we will judge your code :smile:.

#### Git Branches

Give your branch a short descriptive name (like the names between the `<>` below) and prefix the name with something representative for that branch:

   * `feature/<feature-name>` - used when an enhancement or new feature was implemented;
   * `docs/<what-the-docs>` - missing docs or keeping them up to date;
   * `bugfix/<caught-it>` - solved a bug;
   * `test/<thank-you>` - adding missing tests for a feature, we would prefer they would come with the `feature` but still `thank you`;
   * `refactor/<that-name-is-confusing>` - well we hope we don't mess anything and we don't get to use this;
   * `hotfix/<oh-no>` - for when things needed to be fixed yesterday.


### Coding conventions

We do optimize for readability, and it would be awesome if you go through the code and see what conventions we've used so far, some are also explained here:

* Indentation should be 4 *spaces*, besides html, for which it's 2
* 80 character limit is almost strict, but

    - Can be broken in documentation when hyperlinks go over the limits
    - Can be broken in html files
    - Can be broken in js files, but only in html templates

* Python

    - [PEP8](https://www.python.org/dev/peps/pep-0008/) and [PEP257](https://www.python.org/dev/peps/pep-0257/) are followed with small variations
        * Lines are broken after logical operators, not before
        * Multiline docstring has a newline after quote marks, the summary doesn't come directly after.

* Javascript

    - Function names use camelCase
    - Opening brace goes on the line of definition
    - All statements that can, should end with a semicolon ``;``, even
        when not strictly required
    - Code should work in browser as-is, no compilation or building
        required
    - Vue templates intentionally break indentation to improve
        readability (by starting from bottom indentation level)
    - Use template strings for multiline strings

* HTML (also concerns HTML templates in Javascript)

    - Each attribute should go on their own line if there are more than
        two attributes present

* We like to keep things simple, so when possible avoid importing any big libraries.

Thanks,
CSC Developers
