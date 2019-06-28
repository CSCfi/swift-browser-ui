## How to contribute

If you're reading this, it means you saw something that is not right, you want to add a new feature or your manager asked you to contribute to this. In any case we are glad and it would be awesome if you can contribute.

### Testing

We have unit tests and currently no integration tests, and always in need of more. In our Git workflow unit tests are run on every Push and Merge Request.

### Submitting Issues

We have templates for submitting new issues, that you can fill out. For example if you found a bug, use the Bug Report template

### Submitting changes

When you made some changes you are happy with please send a [GitLab merge Request to s3-object-browser](https://gitlab.csc.fi/CSCCSDP/s3-object-browser/merge_requests/new) with a clear list of what you've done (read more about [merge requests](https://docs.gitlab.com/ee/gitlab-basics/add-merge-request.html)). When you create that Merge Request, we will forever be in your debt if you check previous docs for typos.

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

We do optimize for readability, and it would be awesome if you go through the code and see what conventions we used so far:

  * We follow [pep8](https://www.python.org/dev/peps/pep-0008/) and [pep257](https://www.python.org/dev/peps/pep-0257/) with small exceptions;
  * We like to keep things simple, so when possible avoid importing any big libraries.

Thanks,
CSC Developers
