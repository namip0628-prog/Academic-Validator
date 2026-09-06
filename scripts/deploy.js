const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("-------------------------------------------------------");
  console.log("Deploying AcademicValidator Smart Contract...");

  const [deployer] = await hre.ethers.getSigners();
  console.log(`Deployer Account: ${deployer.address}`);

  const AcademicValidator = await hre.ethers.getContractFactory("AcademicValidator");
  const contract = await AcademicValidator.deploy();
  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log(`✓ AcademicValidator deployed successfully to: ${contractAddress}`);

  // Save deployment artifact for Web3.py backend
  const deploymentInfo = {
    address: contractAddress,
    deployer: deployer.address,
    network: hre.network.name,
    chainId: hre.network.config.chainId || 1337,
    deployedAt: new Date().toISOString(),
  };

  const outputPath = path.join(__dirname, "..", "contracts", "deployed_contract.json");
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`✓ Deployment details saved to: ${outputPath}`);
  console.log("-------------------------------------------------------");
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
