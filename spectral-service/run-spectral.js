const { execSync } = require('child_process');

try {
  const result = execSync('npx @stoplight/spectral-cli lint openapi.yaml --ruleset spectral.yaml --format json --verbose', {
    encoding: 'utf8',
    cwd: __dirname
  });
  console.log(result);
} catch (error) {
  console.error('Error running Spectral:', error.message);
  console.error('Exit code:', error.status);
  console.error('Output:', error.stdout);
  console.error('Error output:', error.stderr);
}
