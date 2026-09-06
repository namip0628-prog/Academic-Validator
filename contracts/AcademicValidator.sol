// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AcademicValidator
 * @notice Stores cryptographic SHA-256 fingerprints of academic credentials alongside
 * verified metadata and block timestamps for decentralized authenticity verification.
 *
 * IMPORTANT PRIVACY NOTE:
 * In accordance with student privacy standards and EVM storage optimization,
 * actual document files/images are NEVER stored on-chain. Only the 32-byte SHA-256 hash
 * and verified metadata are anchored on the blockchain.
 */
contract AcademicValidator {
    address public owner;
    uint256 public totalDocuments;

    struct DocumentRecord {
        bytes32 documentHash;      // 32-byte SHA-256 document fingerprint
        string studentName;        // Extracted / Verified Student Name
        string studentId;          // USN / Roll Number / Registration ID
        string institution;        // University / College / Awarding Body
        string course;             // Degree / Program
        string marks;              // CGPA / Grade / Percentage
        uint256 timestamp;         // Block timestamp of registration
        address issuer;            // Registrar / Institutional signer address
        bool exists;               // Existence flag
    }

    // Mapping from SHA-256 document hash to record
    mapping(bytes32 => DocumentRecord) private documents;

    // List of all registered document hashes
    bytes32[] private registeredHashes;

    // Events
    event DocumentRegistered(
        bytes32 indexed documentHash,
        string studentId,
        address indexed issuer,
        uint256 timestamp
    );

    constructor() {
        owner = msg.sender;
        totalDocuments = 0;
    }

    /**
     * @notice Registers a new academic document hash on the blockchain.
     * @param _documentHash 32-byte SHA-256 cryptographic digest of document
     * @param _studentName Name of the student
     * @param _studentId USN / Roll number
     * @param _institution Issuing university or college
     * @param _course Degree program
     * @param _marks CGPA, Grade, or Marks scored
     */
    function registerDocument(
        bytes32 _documentHash,
        string calldata _studentName,
        string calldata _studentId,
        string calldata _institution,
        string calldata _course,
        string calldata _marks
    ) external returns (bool) {
        require(_documentHash != bytes32(0), "Invalid document hash");
        require(!documents[_documentHash].exists, "Document hash already registered on blockchain");

        documents[_documentHash] = DocumentRecord({
            documentHash: _documentHash,
            studentName: _studentName,
            studentId: _studentId,
            institution: _institution,
            course: _course,
            marks: _marks,
            timestamp: block.timestamp,
            issuer: msg.sender,
            exists: true
        });

        registeredHashes.push(_documentHash);
        totalDocuments += 1;

        emit DocumentRegistered(_documentHash, _studentId, msg.sender, block.timestamp);
        return true;
    }

    /**
     * @notice Verifies if a document hash exists on-chain and returns its metadata.
     * @param _documentHash SHA-256 hash to query
     */
    function verifyDocument(bytes32 _documentHash)
        external
        view
        returns (
            bool exists,
            string memory studentName,
            string memory studentId,
            string memory institution,
            string memory course,
            string memory marks,
            uint256 timestamp,
            address issuer
        )
    {
        DocumentRecord memory doc = documents[_documentHash];
        if (!doc.exists) {
            return (false, "", "", "", "", "", 0, address(0));
        }
        return (
            true,
            doc.studentName,
            doc.studentId,
            doc.institution,
            doc.course,
            doc.marks,
            doc.timestamp,
            doc.issuer
        );
    }

    /**
     * @notice Lightweight check for document hash registration status.
     */
    function isDocumentRegistered(bytes32 _documentHash) external view returns (bool) {
        return documents[_documentHash].exists;
    }

    /**
     * @notice Returns total number of registered documents.
     */
    function getDocumentCount() external view returns (uint256) {
        return totalDocuments;
    }
}
