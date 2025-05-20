# Contributing to Backstage Using AI

We can use AI to help us shorten the gap of knowlesge between us and Node.

We can deploy Artifactory and Backstage locally, then edit the plugin. Here are the basis of changes based on ChatGPT:

## Step-by-Step Implementation Plan

1. Support multiple repo names in annotations
Change the plugin so that this is valid:

```
metadata:
  annotations:
    jfrog-artifactory/repo-names: repo1,repo2,repo3
So instead of a single repo-name, we allow a comma-separated list (or an array if you prefer to change the format more drastically).
```

2. Update plugin code: parse annotation as array
In the frontend plugin code (likely inside EntityArtifactoryContent.tsx), locate where it reads the annotation, e.g.:

```
const repoName = entity?.metadata?.annotations?.['jfrog-artifactory/repo-name'];
```
Replace it with something like:

```
const repoNames = entity?.metadata?.annotations?.['jfrog-artifactory/repo-names']
  ?.split(',')
  .map(name => name.trim())
  .filter(Boolean);
```
This way, repoNames becomes an array of strings.

3. Iterate over repos and fetch artifact data
Assuming there's a fetchArtifacts(repoName) function or similar, you'll want to do:

```
const [artifactsByRepo, setArtifactsByRepo] = useState<Record<string, ArtifactData[]>>({});

useEffect(() => {
  async function fetchAll() {
    const results: Record<string, ArtifactData[]> = {};
    for (const repo of repoNames) {
      results[repo] = await fetchArtifacts(repo); // You’ll need to ensure this is safe
    }
    setArtifactsByRepo(results);
  }

  if (repoNames?.length) {
    fetchAll();
  }
}, [repoNames]);
```

Now you’ll have an object like:

```
{
  "repo1": [artifact1, artifact2],
  "repo2": [artifact1, artifact2],
}
```
4. Render the UI for each repository
Update the render logic to iterate over each repository and render a section:

```
return (
  <Content>
    {repoNames.map(repo => (
      <Card key={repo}>
        <CardHeader title={`Artifacts from ${repo}`} />
        <CardContent>
          <ArtifactTable artifacts={artifactsByRepo[repo] ?? []} />
        </CardContent>
      </Card>
    ))}
  </Content>
);
```
This assumes you already have a ArtifactTable or similar component.

5. Optional: Allow backward compatibility
If someone still uses:

```
annotations:
  jfrog-artifactory/repo-name: single-repo
```

You might support both:

```
const raw = entity?.metadata?.annotations?.['jfrog-artifactory/repo-names'] ??
            entity?.metadata?.annotations?.['jfrog-artifactory/repo-name'];

const repoNames = raw?.split(',').map(name => name.trim()).filter(Boolean);
```