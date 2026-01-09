.. _developers_release:

============
Release flow
============

#. Checkout a branch ``release/X.X.X`` (with the new version number)
#. In the root folder, use ``bump-my-version show-bump`` to show the possibilities, for example:

    .. code:: bash

        bump-my-version show-bump
                                                                                                                    
            0.1.0 ── bump ─┬─ major ─ 1.0.0
                        ├─ minor ─ 0.2.0
                        ├─ patch ─ 0.1.1
                        ├─ pre_l ─ invalid: The part has already the maximum value among ['', 'alpha', 'beta', 'rc', 'final'] and cannot be bumped.
                        ╰─ pre_n ─ 0.1.0-final.1

#. Bump the version. For example ``bump-my-version bump major``.
#. In the ``frontend/`` folder, run ``npm install`` to also update the ``package-lock.json`` file after the ``package.json`` has been bumped.
#. In the ``backend/`` folder, run ``./bin/make_translations.sh`` and check if any translations need changing.
#. In the ``backend/`` folder, run ``./bin/update_oas.sh`` to update the OAS.
#. Update the ``CHANGELOG.md`` file.
#. Commit the changes and push the branch.
#. Once the branch is approved, merge it into main.
#. Create a tag with ``git tag -a 1.0.0 -m ":bookmark: Release 1.0.0"``. 
#. Push the tag with ``git push origin 1.0.0``.
#. Once the new image has been pushed to Dockerhub, celebrate! 🎉