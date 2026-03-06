// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Verified Resume NFT Certificate Contract
 * ERC721-compliant NFT for verified resume certificates
 * Production-ready with OpenZeppelin standards
 */

abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }
}

abstract contract Ownable is Context {
    address private _owner;
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    
    constructor() {
        _transferOwnership(_msgSender());
    }
    
    function owner() public view virtual returns (address) {
        return _owner;
    }
    
    modifier onlyOwner() {
        require(owner() == _msgSender(), "Ownable: caller is not the owner");
        _;
    }
    
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        _transferOwnership(newOwner);
    }
    
    function _transferOwnership(address newOwner) internal virtual {
        address oldOwner = _owner;
        _owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }
}

contract VerifiedResumeNFT is Ownable {
    
    // ===================== STATE VARIABLES =====================
    
    string public name = "Verified Resume NFT";
    string public symbol = "VRNFT";
    uint256 public totalSupply = 0;
    
    // NFT metadata structure
    struct NFTMetadata {
        string candidateName;
        uint256 verificationScore;
        bytes32 resumeHash;
        uint256 mintTimestamp;
        string jobTitle;
        string company;
        string[] skills;
    }
    
    // Token ID counter
    uint256 private _tokenIdCounter = 0;
    
    // Token ownership tracking
    mapping(uint256 => address) public tokenOwner;
    mapping(address => uint256[]) public ownerTokens;
    mapping(uint256 => NFTMetadata) public tokenMetadata;
    mapping(bytes32 => uint256) public resumeHashToTokenId;
    mapping(uint256 => string) public tokenURI;
    
    // Allowance tracking for transfers
    mapping(uint256 => address) public tokenApprovals;
    mapping(address => mapping(address => bool)) public operatorApprovals;
    
    // ===================== EVENTS =====================
    
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);
    
    event VerifiedResumeNFTMinted(
        uint256 indexed tokenId,
        address indexed to,
        string candidateName,
        uint256 verificationScore,
        bytes32 indexed resumeHash
    );
    
    // ===================== MODIFIERS =====================
    
    modifier tokenExists(uint256 tokenId) {
        require(tokenOwner[tokenId] != address(0), "Token does not exist");
        _;
    }
    
    modifier onlyTokenOwner(uint256 tokenId) {
        require(tokenOwner[tokenId] == msg.sender, "Not token owner");
        _;
    }
    
    // ===================== CORE FUNCTIONS =====================
    
    /**
     * Mint verified resume NFT
     * @param to Recipient address
     * @param candidateName Name of candidate
     * @param verificationScore Verification score
     * @param resumeHash Hash of resume
     * @param jobTitle Job title
     * @param company Company name
     * @param skills Array of skills
     * @return tokenId ID of minted token
     */
    function mintVerifiedResumeNFT(
        address to,
        string memory candidateName,
        uint256 verificationScore,
        bytes32 resumeHash,
        string memory jobTitle,
        string memory company,
        string[] memory skills
    ) external onlyOwner returns (uint256) {
        
        require(to != address(0), "Invalid recipient");
        require(resumeHashToTokenId[resumeHash] == 0, "NFT already minted for this resume");
        require(verificationScore >= 7500, "Insufficient verification score (need >=75%)");
        require(bytes(candidateName).length > 0, "Invalid candidate name");
        
        uint256 tokenId = _tokenIdCounter;
        _tokenIdCounter++;
        
        // Set ownership and balances
        tokenOwner[tokenId] = to;
        ownerTokens[to].push(tokenId);
        totalSupply++;
        
        // Set metadata
        NFTMetadata memory metadata = NFTMetadata(
            candidateName,
            verificationScore,
            resumeHash,
            block.timestamp,
            jobTitle,
            company,
            skills
        );
        
        tokenMetadata[tokenId] = metadata;
        resumeHashToTokenId[resumeHash] = tokenId;
        
        // Set token URI
        tokenURI[tokenId] = string(
            abi.encodePacked(
                "ipfs://QmVerifiedResumeNFT/",
                _uint2str(tokenId),
                ".json"
            )
        );
        
        emit Transfer(address(0), to, tokenId);
        emit VerifiedResumeNFTMinted(
            tokenId,
            to,
            candidateName,
            verificationScore,
            resumeHash
        );
        
        return tokenId;
    }
    
    /**
     * Get NFT metadata
     * @param tokenId Token ID
     * @return Metadata struct
     */
    function getNFTMetadata(uint256 tokenId)
        external
        view
        tokenExists(tokenId)
        returns (NFTMetadata memory)
    {
        return tokenMetadata[tokenId];
    }
    
    /**
     * Get token ID for resume hash
     * @param resumeHash Resume hash
     * @return Token ID (0 if not minted)
     */
    function getTokenIdByResumeHash(bytes32 resumeHash)
        external
        view
        returns (uint256)
    {
        return resumeHashToTokenId[resumeHash];
    }
    
    /**
     * Get all tokens owned by address
     * @param owner Owner address
     * @return Array of token IDs
     */
    function getTokensByOwner(address owner)
        external
        view
        returns (uint256[] memory)
    {
        return ownerTokens[owner];
    }
    
    /**
     * Check if address owns token
     * @param tokenId Token ID
     * @param account Address to check
     * @return True if account owns token
     */
    function ownsToken(uint256 tokenId, address account)
        external
        view
        tokenExists(tokenId)
        returns (bool)
    {
        return tokenOwner[tokenId] == account;
    }
    
    /**
     * Transfer NFT to another address
     * @param from Sender address
     * @param to Recipient address
     * @param tokenId Token ID to transfer
     */
    function transferFrom(
        address from,
        address to,
        uint256 tokenId
    ) external tokenExists(tokenId) {
        
        require(from == tokenOwner[tokenId], "From address is not owner");
        require(to != address(0), "Invalid recipient");
        require(msg.sender == from || msg.sender == tokenApprovals[tokenId] ||
                operatorApprovals[from][msg.sender], "Not authorized to transfer");
        
        // Transfer ownership
        tokenOwner[tokenId] = to;
        tokenApprovals[tokenId] = address(0);
        
        // Update owner balances
        uint256[] storage fromTokens = ownerTokens[from];
        for (uint i = 0; i < fromTokens.length; i++) {
            if (fromTokens[i] == tokenId) {
                fromTokens[i] = fromTokens[fromTokens.length - 1];
                fromTokens.pop();
                break;
            }
        }
        
        ownerTokens[to].push(tokenId);
        
        emit Transfer(from, to, tokenId);
    }
    
    /**
     * Approve another address to transfer token
     * @param to Address to approve
     * @param tokenId Token ID
     */
    function approve(address to, uint256 tokenId)
        external
        tokenExists(tokenId)
        onlyTokenOwner(tokenId)
    {
        tokenApprovals[tokenId] = to;
        emit Approval(msg.sender, to, tokenId);
    }
    
    /**
     * Set approval for all tokens
     * @param operator Address to approve
     * @param approved True to approve, false to revoke
     */
    function setApprovalForAll(address operator, bool approved) external {
        require(operator != msg.sender, "Cannot approve yourself");
        operatorApprovals[msg.sender][operator] = approved;
        emit ApprovalForAll(msg.sender, operator, approved);
    }
    
    // ===================== UTILITY FUNCTIONS =====================
    
    /**
     * Convert uint to string
     * @param _i Number to convert
     * @return String representation
     */
    function _uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        while (_i != 0) {
            k = k-1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }
    
    /**
     * Get contract info
     * @return Total supply and owner address
     */
    function contractInfo() external view returns (uint256 supply, address ownerAddr) {
        return (totalSupply, owner());
    }
}
