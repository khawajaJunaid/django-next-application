import React, { useState, ChangeEvent } from 'react';
import Layout from '../components/Layout';
import { Card, CardContent, Typography, Button, Box, CircularProgress } from '@material-ui/core';
import Alert from '@material-ui/lab/Alert';
import { useAuth } from '../auth';

const cardStyle = {
  maxWidth: 400,
  margin: '0 auto',
  padding: '20px',
  boxShadow: '0 4px 8px 0 rgba(0, 0, 0, 0.2)',
  borderRadius: '8px',
};

const LoaderOverlay = () => (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999, // Ensure it's above other content
    }}
  >
    <CircularProgress color="secondary" size={100} thickness={2} />
  </div>
);

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { loading, getToken, isAuthenticated } = useAuth();
  const [apiError, setApiError] = useState<string | null>(null);
  const [responseData, setResponseData] = useState<any>(null);
  const [loadingResponse, setLoadingResponse] = useState(false);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files[0];
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    setError(null);
    setUploading(true);
    setApiError(null);
    setLoadingResponse(true);

    const formData = new FormData();
    formData.append('pdf_file', selectedFile as File);

    try {
      const token = await getToken();
      if (!token) {
        setError('Authorization token not available.');
        setUploading(false);
        setLoadingResponse(false);
        return;
      }
      const url = process.env.NEXT_PUBLIC_API_HOST + '/upload_file';
      fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => {
          if (response.ok) {
            console.log('File uploaded successfully');
            setUploading(false);
            setSelectedFile(null);

            // Assuming the API returns JSON data with the structure you provided
            response.json().then((data) => {
              setResponseData(data);
              setLoadingResponse(false);
            });
          } else {
            console.error('Error uploading file:', response.statusText);
            // Display the API response error if available
            response.json().then((text) => {
              setApiError(text);
              setUploading(false);
              setLoadingResponse(false);
            }).catch((err) => {
              console.error('Error parsing API response:', err);
              setError('An error occurred while processing the API response.');
              setUploading(false);
              setLoadingResponse(false);
            });
          }
        })
        .catch((err) => {
          console.error('Fetch error:', err);
          setError(`An error occurred while uploading the file: ${err}`);
          setUploading(false);
          setLoadingResponse(false);
        });
    } catch (err) {
      setError(`An error occurred while uploading the file: ${err}`);
      console.error('Error uploading file:', err);
      setUploading(false);
      setLoadingResponse(false);
    }
  };

  return (
    <Layout>
      {uploading ? <LoaderOverlay /> : (
        <>
          <Card style={cardStyle}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                File Upload
              </Typography>
              {error && <Alert severity="error">{error}</Alert>}
              {apiError && <Alert severity="error">{apiError}</Alert>}
              <input
                type="file"
                id="fileInput"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              {selectedFile && (
                <Typography variant="body1" gutterBottom>
                  Selected File: {selectedFile.name}
                </Typography>
              )}
              <Box display="flex" justifyContent="space-between">
                <label htmlFor="fileInput">
                  <Button
                    variant="contained"
                    component="span"
                    disabled={uploading}
                  >
                    {uploading ? 'Uploading...' : 'Choose File'}
                  </Button>
                </label>
                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={uploading || !selectedFile}
                >
                  {uploading ? 'Uploading...' : 'Upload File'}
                </Button>
              </Box>
            </CardContent>
          </Card>
          <Card style={cardStyle}>
            <CardContent>
              {loadingResponse ? (
                <CircularProgress />
              ) : responseData ? (
                <div>
                  <Typography variant="body1" gutterBottom>
                    Response Details:
                  </Typography>
                  <ul>
                    <li>ID: {responseData.id}</li>
                    <li>Name: {responseData.name}</li>
                    <li>Address: {responseData.address}</li>
                    <li>Income: {responseData.income}</li>
                  </ul>
                </div>
              ) : null}
            </CardContent>
          </Card>
        </>
      )}
    </Layout>
  );
};

export default FileUpload;
