// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ResumeVerificationRegistry
 * @dev Smart contract for storing verified resume claims on blockchain
 * @notice Immutable record of resume verification results for authenticity
 */

contract ResumeVerificationRegistry {
    
    // ===================== DATA STRUCTURES =====================
    
    struct VerifiedClaim {
        bytes32 claimHash;              // Hash of claim + verification data
        address verifier;               // Address that verified the claim
        uint256 timestamp;              // When claim was verified
        uint8 trustScore;               // 0-100
        bool isValid;                   // Validity flag
        string claimText;               // Original claim text
        uint256 verificationCount;      // Number of verifications
    }
    
    struct ResumeRecord {
        bytes32 resumeHash;             // Hash of entire resume
        address resumeOwner;            // User who submitted resume
        uint256 createdAt;              // When record was created
        uint256 totalClaims;            // Number of claims verified
        uint256 avgTrustScore;          // Average trust score
        bytes32[] claimHashes;          // Array of claim hashes
        bool isVisible;                 // Privacy flag
    }
    
    // ===================== STATE VARIABLES =====================
    
    mapping(bytes32 => VerifiedClaim) public claims;           // claim hash => claim data
    mapping(address => bytes32[]) public userClaims;          // user => claim hashes
    mapping(bytes32 => ResumeRecord) public resumeRecords;    // resume hash => resume data
    mapping(address => bytes32[]) public userResumes;         // user => resume hashes
    mapping(address => bool) public verifiers;                // authorized verifiers
    mapping(bytes32 => uint256) public claimVerificationCount; // claim hash => count
    
    address public owner;
    uint256 public totalClaimsVerified;
    uint256 public totalResumesSubmitted;
    
    // ===================== EVENTS =====================
    
    event ClaimRegistered(
        bytes32 indexed claimHash,
        address indexed verifier,
        bytes32 indexed resumeHash,
        uint8 trustScore,
        uint256 timestamp
    );
    
    event ResumeRecordCreated(
        bytes32 indexed resumeHash,
        address indexed owner,
        uint256 totalClaims,
        uint256 timestamp
    );
    
    event VerifierAuthorized(address indexed verifier, uint256 timestamp);
    event VerifierRevoked(address indexed verifier, uint256 timestamp);
    event ClaimInvalidated(bytes32 indexed claimHash, uint256 timestamp);
    
    // ===================== MODIFIERS =====================
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    modifier onlyVerifier() {
        require(verifiers[msg.sender], "Only authorized verifiers can call this");
        _;
    }
    
    modifier validTrustScore(uint8 _score) {
        require(_score >= 0 && _score <= 100, "Trust score must be 0-100");
        _;
    }
    
    // ===================== CONSTRUCTOR =====================
    
    constructor() {
        owner = msg.sender;
        verifiers[msg.sender] = true;
        totalClaimsVerified = 0;
        totalResumesSubmitted = 0;
    }
    
    // ===================== VERIFIER MANAGEMENT =====================
    
    /**
     * @dev Authorize an address as verifier
     * @param _verifier Address to authorize
     */
    function authorizeVerifier(address _verifier) external onlyOwner {
        require(_verifier != address(0), "Invalid address");
        verifiers[_verifier] = true;
        emit VerifierAuthorized(_verifier, block.timestamp);
    }
    
    /**
     * @dev Revoke verifier authorization
     * @param _verifier Address to revoke
     */
    function revokeVerifier(address _verifier) external onlyOwner {
        verifiers[_verifier] = false;
        emit VerifierRevoked(_verifier, block.timestamp);
    }
    
    // ===================== CLAIM REGISTRATION =====================
    
    /**
     * @dev Register a verified claim on blockchain
     * @param _claimHash Keccak256 hash of claim data
     * @param _trustScore Trust score (0-100)
     * @param _claimText Original claim text
     * @param _resumeHash Hash of the resume this claim belongs to
     */
    function registerClaim(
        bytes32 _claimHash,
        uint8 _trustScore,
        string memory _claimText,
        bytes32 _resumeHash
    ) external onlyVerifier validTrustScore(_trustScore) {
        
        require(_claimHash != bytes32(0), "Invalid claim hash");
        require(!claims[_claimHash].isValid || claims[_claimHash].timestamp == 0, 
            "Claim already registered");
        
        VerifiedClaim memory newClaim = VerifiedClaim({
            claimHash: _claimHash,
            verifier: msg.sender,
            timestamp: block.timestamp,
            trustScore: _trustScore,
            isValid: true,
            claimText: _claimText,
            verificationCount: 1
        });
        
        claims[_claimHash] = newClaim;
        userClaims[msg.sender].push(_claimHash);
        totalClaimsVerified++;
        
        emit ClaimRegistered(_claimHash, msg.sender, _resumeHash, _trustScore, block.timestamp);
    }
    
    /**
     * @dev Register multiple claims for a resume
     * @param _claimHashes Array of claim hashes
     * @param _trustScores Array of trust scores
     * @param _claimTexts Array of claim texts
     * @param _resumeHash Hash of the resume
     */
    function registerBatchClaims(
        bytes32[] memory _claimHashes,
        uint8[] memory _trustScores,
        string[] memory _claimTexts,
        bytes32 _resumeHash
    ) external onlyVerifier {
        
        require(_claimHashes.length == _trustScores.length, "Array length mismatch");
        require(_claimHashes.length == _claimTexts.length, "Array length mismatch");
        require(_claimHashes.length > 0, "Empty array");
        require(_claimHashes.length <= 100, "Too many claims");
        
        for (uint i = 0; i < _claimHashes.length; i++) {
            registerClaim(_claimHashes[i], _trustScores[i], _claimTexts[i], _resumeHash);
        }
    }
    
    // ===================== RESUME RECORD MANAGEMENT =====================
    
    /**
     * @dev Create a resume verification record
     * @param _resumeHash Hash of the resume
     * @param _totalClaims Number of claims in resume
     * @param _avgTrustScore Average trust score
     * @param _claimHashes Array of verified claim hashes
     */
    function createResumeRecord(
        bytes32 _resumeHash,
        uint256 _totalClaims,
        uint256 _avgTrustScore,
        bytes32[] memory _claimHashes
    ) external onlyVerifier {
        
        require(_resumeHash != bytes32(0), "Invalid resume hash");
        require(!resumeRecords[_resumeHash].isVisible || resumeRecords[_resumeHash].createdAt == 0,
            "Resume already recorded");
        require(_totalClaims > 0, "Must have claims");
        require(_avgTrustScore <= 100, "Invalid trust score");
        
        ResumeRecord memory record = ResumeRecord({
            resumeHash: _resumeHash,
            resumeOwner: msg.sender,
            createdAt: block.timestamp,
            totalClaims: _totalClaims,
            avgTrustScore: _avgTrustScore,
            claimHashes: _claimHashes,
            isVisible: true
        });
        
        resumeRecords[_resumeHash] = record;
        userResumes[msg.sender].push(_resumeHash);
        totalResumesSubmitted++;
        
        emit ResumeRecordCreated(_resumeHash, msg.sender, _totalClaims, block.timestamp);
    }
    
    // ===================== CLAIM VERIFICATION =====================
    
    /**
     * @dev Get claim details
     * @param _claimHash Hash of the claim
     */
    function getClaim(bytes32 _claimHash) external view returns (VerifiedClaim memory) {
        require(claims[_claimHash].isValid, "Claim not found");
        return claims[_claimHash];
    }
    
    /**
     * @dev Verify claim authenticity by checking blockchain
     * @param _claimHash Hash to verify
     * @return isValid Whether claim is valid and registered
     * @return trustScore The trust score assigned
     * @return verificationTime When claim was verified
     */
    function verifyClaim(bytes32 _claimHash) 
        external 
        view 
        returns (bool isValid, uint8 trustScore, uint256 verificationTime) 
    {
        VerifiedClaim memory claim = claims[_claimHash];
        return (claim.isValid, claim.trustScore, claim.timestamp);
    }
    
    /**
     * @dev Get resume record
     * @param _resumeHash Hash of the resume
     */
    function getResumeRecord(bytes32 _resumeHash) 
        external 
        view 
        returns (ResumeRecord memory) 
    {
        require(resumeRecords[_resumeHash].isVisible, "Resume record not found");
        return resumeRecords[_resumeHash];
    }
    
    /**
     * @dev Batch verify multiple claims
     * @param _claimHashes Array of claim hashes to verify
     */
    function batchVerifyClaims(bytes32[] memory _claimHashes)
        external
        view
        returns (bool[] memory validities, uint8[] memory scores)
    {
        validities = new bool[](_claimHashes.length);
        scores = new uint8[](_claimHashes.length);
        
        for (uint i = 0; i < _claimHashes.length; i++) {
            VerifiedClaim memory claim = claims[_claimHashes[i]];
            validities[i] = claim.isValid;
            scores[i] = claim.trustScore;
        }
        
        return (validities, scores);
    }
    
    // ===================== CLAIM INVALIDATION =====================
    
    /**
     * @dev Invalidate a previously verified claim
     * @param _claimHash Hash of claim to invalidate
     */
    function invalidateClaim(bytes32 _claimHash) external onlyVerifier {
        require(claims[_claimHash].isValid, "Claim not found");
        require(claims[_claimHash].verifier == msg.sender || msg.sender == owner, 
            "Only claim verifier or owner can invalidate");
        
        claims[_claimHash].isValid = false;
        emit ClaimInvalidated(_claimHash, block.timestamp);
    }
    
    // ===================== PRIVACY =====================
    
    /**
     * @dev Set resume visibility
     * @param _resumeHash Hash of resume
     * @param _isVisible Visibility flag
     */
    function setResumeVisibility(bytes32 _resumeHash, bool _isVisible) external {
        require(resumeRecords[_resumeHash].resumeOwner == msg.sender || msg.sender == owner,
            "Only owner can change visibility");
        
        resumeRecords[_resumeHash].isVisible = _isVisible;
    }
    
    // ===================== STATISTICS =====================
    
    /**
     * @dev Get total verified claims count
     */
    function getTotalClaimsVerified() external view returns (uint256) {
        return totalClaimsVerified;
    }
    
    /**
     * @dev Get total resumes submitted
     */
    function getTotalResumesSubmitted() external view returns (uint256) {
        return totalResumesSubmitted;
    }
    
    /**
     * @dev Get user's claim count
     * @param _user Address of user
     */
    function getUserClaimsCount(address _user) external view returns (uint256) {
        return userClaims[_user].length;
    }
    
    /**
     * @dev Get user's resume count
     * @param _user Address of user
     */
    function getUserResumesCount(address _user) external view returns (uint256) {
        return userResumes[_user].length;
    }
    
    /**
     * @dev Get average trust score across all verified claims
     */
    function getAverageTrustScore() external view returns (uint256) {
        if (totalClaimsVerified == 0) return 0;
        
        uint256 totalScore = 0;
        // This is a simplified version - in production, use events or off-chain indexing
        
        return totalScore / totalClaimsVerified;
    }
    
    // ===================== EMERGENCY =====================
    
    /**
     * @dev Emergency pause by owner
     * Note: In production, use a Pausable pattern from OpenZeppelin
     */
    function pause() external onlyOwner {
        // Implementation
    }
    
    function unpause() external onlyOwner {
        // Implementation
    }
}
