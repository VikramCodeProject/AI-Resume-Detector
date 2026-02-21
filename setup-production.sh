#!/bin/bash
# Production Deployment Setup Script
# Run this script to prepare your project for production deployment

set -e  # Exit on error

echo "============================================"
echo "Resume Verification System"
echo "Production Deployment Setup"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to create a new production .env? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
    else
        cp .env.production .env
        echo -e "${GREEN}✓${NC} Created new .env from production template"
    fi
else
    cp .env.production .env
    echo -e "${GREEN}✓${NC} Created .env from production template"
fi

echo ""
echo "============================================"
echo "Generating Secure Secrets"
echo "============================================"

# Generate JWT secret
if command -v python3 &> /dev/null; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    echo -e "${GREEN}✓${NC} Generated JWT_SECRET: ${JWT_SECRET:0:16}..."
    echo -e "${GREEN}✓${NC} Generated SECRET_KEY: ${SECRET_KEY:0:16}..."
    
    # Update .env file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET}/" .env
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    else
        # Linux
        sed -i "s/JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET}/" .env
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    fi
    
    echo -e "${GREEN}✓${NC} Updated .env with secure secrets"
else
    echo -e "${RED}✗${NC} Python3 not found. Please manually generate secrets:"
    echo "  python -c \"import secrets; print(secrets.token_hex(32))\""
fi

echo ""
echo "============================================"
echo "Checklist - Manual Steps Required"
echo "============================================"
echo ""
echo "You still need to configure these in .env:"
echo ""
echo "  ${YELLOW}1. DATABASE_URL${NC} - Your production database connection"
echo "  ${YELLOW}2. REDIS_URL${NC} - Your production Redis instance"
echo "  ${YELLOW}3. GITHUB_API_KEY${NC} - Get from: https://github.com/settings/tokens"
echo "  ${YELLOW}4. AWS_ACCESS_KEY_ID${NC} - Your AWS credentials"
echo "  ${YELLOW}5. AWS_SECRET_ACCESS_KEY${NC} - Your AWS secret"
echo "  ${YELLOW}6. AWS_S3_BUCKET${NC} - Your S3 bucket name"
echo "  ${YELLOW}7. ETH_RPC_URL${NC} - Blockchain RPC endpoint (Alchemy/Infura)"
echo "  ${YELLOW}8. SMART_CONTRACT_ADDRESS${NC} - Your deployed contract address"
echo "  ${YELLOW}9. PRIVATE_KEY${NC} - Blockchain wallet private key"
echo "  ${YELLOW}10. ALLOWED_ORIGINS${NC} - Your production domain(s)"
echo ""
echo "Edit with: nano .env  (or vim/code)"
echo ""

echo "============================================"
echo "Docker Images"
echo "============================================"
echo ""
read -p "Build Docker images now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Building images..."
    docker-compose -f docker-compose.production.yml build
    echo -e "${GREEN}✓${NC} Docker images built successfully"
else
    echo "Skipped. Build later with:"
    echo "  docker-compose -f docker-compose.production.yml build"
fi

echo ""
echo "============================================"
echo "SSL/TLS Certificates"
echo "============================================"
echo ""
echo "For HTTPS, you need SSL certificates. Options:"
echo ""
echo "  1. Let's Encrypt (Free, recommended):"
echo "     sudo certbot --nginx -d yourdomain.com"
echo ""
echo "  2. CloudFlare (Free, with CDN):"
echo "     Use CloudFlare as reverse proxy"
echo ""
echo "  3. Purchase certificate:"
echo "     From SSL vendors (DigiCert, Comodo, etc.)"
echo ""

echo "============================================"
echo "Deployment Commands"
echo "============================================"
echo ""
echo "To deploy with Docker Compose:"
echo "  ${GREEN}docker-compose -f docker-compose.production.yml up -d${NC}"
echo ""
echo "To check status:"
echo "  ${GREEN}docker-compose -f docker-compose.production.yml ps${NC}"
echo ""
echo "To view logs:"
echo "  ${GREEN}docker-compose -f docker-compose.production.yml logs -f${NC}"
echo ""
echo "To stop:"
echo "  ${GREEN}docker-compose -f docker-compose.production.yml down${NC}"
echo ""

echo "============================================"
echo "Next Steps"
echo "============================================"
echo ""
echo "1. Edit .env with your production values"
echo "2. Set up managed database (AWS RDS, DigitalOcean, etc.)"
echo "3. Configure SSL/TLS certificates"
echo "4. Deploy: docker-compose -f docker-compose.production.yml up -d"
echo "5. Set up monitoring and backups"
echo "6. Configure domain DNS"
echo ""
echo "For detailed instructions, see:"
echo "  ${GREEN}PRODUCTION_DEPLOYMENT.md${NC}"
echo ""
echo "============================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================"
