
def extract_source_code_repositories(packages_information):
    repositories = []
    errors = []

    for package in packages_information:

        try:
            source_code_uri = package['source_code_uri']
            homepage_uri    = package['homepage_uri']

            if source_code_uri is not None and source_code_uri != '' and ("github" in source_code_uri or "gitlab" in source_code_uri or "git" in source_code_uri):
                # repositories.append(source_code_uri)
                repositories.append('/'.join(source_code_uri.split('/')[:5]))

            elif homepage_uri is not None and homepage_uri != '':

                if "github.com" in homepage_uri:
                    repositories.append('/'.join(homepage_uri.split('/')[:5]))

                elif "gitlab.com" in homepage_uri:
                    repositories.append('/'.join(homepage_uri.split('/')[:5]))

                else:
                    errors.append(package)

            else:
                errors.append(package)
        except KeyError:
            errors.append(package)
    return repositories, errors
