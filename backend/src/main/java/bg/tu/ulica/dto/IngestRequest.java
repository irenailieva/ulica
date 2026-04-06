package bg.tu.ulica.dto;

public class IngestRequest {
    private String sourcePlatform;
    private String externalId;
    private String rawText;
    private String rawImages; // JSON string or map

    // Getters and setters
    public String getSourcePlatform() { return sourcePlatform; }
    public void setSourcePlatform(String sourcePlatform) { this.sourcePlatform = sourcePlatform; }
    
    public String getExternalId() { return externalId; }
    public void setExternalId(String externalId) { this.externalId = externalId; }
    
    public String getRawText() { return rawText; }
    public void setRawText(String rawText) { this.rawText = rawText; }
    
    public String getRawImages() { return rawImages; }
    public void setRawImages(String rawImages) { this.rawImages = rawImages; }
}
