# Mauritius Digital Form - Complete Test Workflow

## URL
- **Form URL:** http://test.digitalform-mauritius.com.test1.1evis.net/
- **Environment:** Test Environment (Test 1)
- **Related Issue:** VISASGF-2864 (French Translation Fix)

## Complete Test Data

### Step 1: Submit Application Online

#### Personal Details Section
```
First Name:              Jean
Last Name:               Dupont
Gender:                  Male
Date of Birth:           15/01/1990
Country of Residence:    Mauritius
Residential Address:     123 Royal Street, Port Louis
```

#### Passport and Contact Details
```
Country of Passport:     France
Passport Number:         A12345678
Email Address:           applicant@gmail.com
Confirm Email Address:   applicant@gmail.com
Mobile/Cell Phone:       +230 57123456
```

#### Travel Details
```
Intended Date of Entry:  15/05/2026
Type of Transport:       By air
Airline Company:         AIR MAURITIUS
Flight Number:           MK015
Last City/Port of Embarkation: Paris
```

#### Health Declaration
```
Fever:                   No
Skin lesions:            No
Joints pain:             No
Sore throat:             No
Cough:                   No
Breathing difficulties:  No
```

#### Declaration of Applicant
```
Declaration checkbox:    ✓ Checked
Terms and Conditions:    ✓ Checked
```

## Form Navigation Flow

1. **Access Form** → Click "Apply Online"
2. **Step 1: Submit Application Online**
   - Fill Personal Details Section
   - Fill Passport and Contact Details
   - Fill Travel Details
   - Answer Health Declaration Questions
   - Check Declaration and Terms checkboxes
   - Click "Next" or "Continue" to proceed to Step 2

3. **Step 2: Review and Confirm Payment**
   - Review all information filled in Step 1
   - Fill in Delivery information (if required)
   - Review payment amount
   - Confirm payment details
   - Proceed to payment gateway or Step 3

4. **Step 3: Receive Approval Confirmation**
   - Confirmation page with application details
   - Approval status message
   - Reference number or confirmation email

## Known Issues Found During Testing

### Translation Issues (VISASGF-2864)
- ❌ **Last Name Field Label:** Shows "Last Name(s) / Surname(s)" in ENGLISH (should be French)
- ❌ **Step Indicators:** All in English:
  - "1. Submit Application Online"
  - "2. Review and Confirm Payment"
  - "3. Receive Approval Confirmation"

### Field Validation Issues
- ⚠️ Date of Birth picker may require specific date format
- ⚠️ Phone number field requires country code (+230 for Mauritius)

## How to Use This for Future Tests

**Using Playwright MCP:**
```bash
# Navigate to form
# Fill fields using test data provided above
# Complete all steps
# Verify translations are in French (after fix)
```

**Using this as a Prompt:**
- Copy the test data section above
- Use Playwright MCP with this workflow
- Verify each step is completed correctly
- Check translation fixes have been applied (French text should replace English)

## Testing Checklist

- [ ] Step 1 - Personal information filled correctly
- [ ] Step 1 - All health questions answered
- [ ] Step 1 - Checkboxes checked
- [ ] Step 2 - Delivery information (if required) filled
- [ ] Step 2 - Payment review page accessible
- [ ] Step 3 - Approval confirmation received
- [ ] French translations applied correctly (after VISASGF-2864 fix)
- [ ] No English phrases mixed in French text
- [ ] All validation errors resolved
- [ ] Form submission successful

## Last Updated
- **Date:** 2026-04-22
- **Tester:** Claude Code + Playwright MCP
- **Status:** Workflow documented, ready for future testing
