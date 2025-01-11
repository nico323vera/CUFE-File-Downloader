from seleniumbase import SB
import os
import pandas as pd
import logging
import time
import shutil
import pdfplumber

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def cufe_classification(path):
    """
    Classify CUFE codes from an Excel file.
    """
    try:
        df = pd.read_excel(path)
        if 'Tipo de documento' not in df.columns or 'CUFE/CUDE' not in df.columns:
            logging.warning("The Excel file does not contain the required columns.")
            return False, []

        # Filter rows where 'Tipo de documento' is 'Factura Electrónica'
        filtered_df = df[df['Tipo de documento'] == 'Factura electrónica']
        cufe_codes = filtered_df['CUFE/CUDE'].dropna().tolist()

        logging.info(f"Extracted {len(cufe_codes)} CUFE codes from the Excel file.")
        return True, cufe_codes
    except Exception as e:
        logging.error(f"Error reading the Excel file: {e}")
        return False, []


def get_payment_type(pdf_path):
    """
    Extracts the "Forma de pago" field from a PDF and returns its value.
    Returns "Contado", "Credito", or None if not found.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Look for the "Forma de pago" field
                    if "Forma de pago" in text:
                        # Extract the value after "Forma de pago"
                        lines = text.splitlines()
                        for line in lines:
                            if "Forma de pago" in line:
                                # Extract and return the value (e.g., "Contado" or "Credito")
                                if "Contado" in line:
                                    return "Contado"
                                elif "Crédito" in line:
                                    return "Crédito"
        return None
    except Exception as e:
        logging.error(f"Error reading PDF {pdf_path}: {e}")
        return None


def relocate_and_classify_file(cufe, source_dir, target_dir):
    """
    Classify and relocate a PDF based on its "Forma de pago" field.
    """
    try:
        # Define the expected filename
        expected_filename = f"{cufe}.pdf"
        source_path = os.path.join(source_dir, expected_filename)

        # Check if the file exists in the source directory
        if os.path.exists(source_path):
            # Determine the payment type from the PDF
            payment_type = get_payment_type(source_path)

            # Create subdirectories for "Contado" and "Credito"
            subdir = os.path.join(target_dir, payment_type if payment_type else "Unclassified")
            if not os.path.exists(subdir):
                os.makedirs(subdir)

            # Move the file to the appropriate subdirectory
            target_path = os.path.join(subdir, expected_filename)
            shutil.move(source_path, target_path)
            logging.info(f"File moved to: {target_path}")
        else:
            logging.warning(f"File for CUFE {cufe} not found in {source_dir}.")
    except Exception as e:
        logging.error(f"Error processing file for CUFE {cufe}: {e}")


def process_cufe_codes(cufe_codes, download_directory, max_retries=3):
    """
    Process CUFE codes to download associated PDFs from the DIAN website,
    classify them based on "Forma de pago," and relocate them.
    Save a .txt file with failed CUFE codes if retries are exhausted.
    """
    default_download_dir = os.path.join(os.getcwd(), "downloaded_files")  # Temporary download folder
    if not os.path.exists(default_download_dir):
        os.makedirs(default_download_dir)

    failed_cufes = []  # Track failed CUFE codes

    with SB(uc=True, test=True) as sb:
        # Open the DIAN website
        url = "https://catalogo-vpfe.dian.gov.co/User/SearchDocument"
        sb.uc_open_with_reconnect(url, 5)

        for idx, cufe in enumerate(cufe_codes):
            attempts = 0  # Track attempts for the current CUFE
            while attempts < max_retries:
                try:
                    logging.info(f"Processing CUFE {idx + 1}/{len(cufe_codes)}: {cufe} (Attempt {attempts + 1}/{max_retries})")

                    # Solve CAPTCHA if necessary (manual intervention might be required initially)
                    if idx == 0 and attempts == 0:  # First CUFE, first attempt
                        logging.info("Ensure CAPTCHA is solved if required.")

                    # Paste CUFE and search
                    sb.type("#DocumentKey", cufe, timeout=5)
                    sb.click('button:contains("Buscar")', timeout=5)

                    # Check if the PDF download link is available
                    try:
                        sb.wait_for_element_visible('a:contains("Descargar PDF")', timeout=5)
                        sb.click_link("Descargar PDF")
                        logging.info(f"PDF successfully downloaded for CUFE: {cufe}")

                        # Classify and relocate the file
                        relocate_and_classify_file(cufe, default_download_dir, download_directory)

                        # If successful, break out of the retry loop
                        break

                    except Exception as e:
                        logging.warning(f"No PDF available for CUFE: {cufe}. Error: {e}")
                        raise

                    # Click the "Volver" link to return to the main page
                    try:
                        sb.wait_for_element_visible('a:contains("Volver")', timeout=5)
                        sb.click_link("Volver")
                        logging.info(f"Returned to the main page for the next CUFE.")
                    except Exception:
                        logging.error(f"Error returning to the main page for CUFE {cufe}.")
                        raise Exception("Failed to navigate back to the main page.")

                    # Optional: Wait between requests to mimic human interaction
                    time.sleep(2)

                except Exception as e:
                    attempts += 1
                    logging.error(f"Error processing CUFE {cufe} on attempt {attempts}: {e}")

                    # Restart browser if retries are needed
                    if attempts < max_retries:
                        logging.info(f"Retrying CUFE {cufe} (Attempt {attempts + 1}/{max_retries})...")
                        sb.uc_open_with_reconnect(url, 5)
                        time.sleep(2)  # Small delay before retrying
                    else:
                        logging.error(f"Maximum retries reached for CUFE {cufe}. Skipping...")
                        failed_cufes.append(cufe)  # Track the failed CUFE
                        break

    # Save failed CUFE codes to a .txt file
    if failed_cufes:
        failed_file_path = os.path.join(download_directory, "failed_cufes.txt")
        try:
            with open(failed_file_path, "w") as file:
                file.write("\n".join(failed_cufes))
            logging.info(f"Failed CUFE codes saved to: {failed_file_path}")
        except Exception as e:
            logging.error(f"Error saving failed CUFE codes: {e}")

    logging.info("Processing completed.")
