package bg.tu.ulica.model;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;

@Entity
@Table(name = "raw_scrapes")
public class RawScrape {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "source_platform", nullable = false, length = 50)
    private String sourcePlatform;

    @Column(name = "external_id", unique = true, length = 100)
    private String externalId;

    @Column(name = "raw_text", nullable = false, columnDefinition = "TEXT")
    private String rawText;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "raw_images", columnDefinition = "jsonb")
    private String rawImages; // Can use a custom class or Map depending on needs, String is fine for raw JSON

    @CreationTimestamp
    @Column(name = "scrape_timestamp", updatable = false)
    private LocalDateTime scrapeTimestamp;

    @Column(name = "status", length = 20)
    private String status = "PENDING";

    public RawScrape() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSourcePlatform() {
        return sourcePlatform;
    }

    public void setSourcePlatform(String sourcePlatform) {
        this.sourcePlatform = sourcePlatform;
    }

    public String getExternalId() {
        return externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public String getRawText() {
        return rawText;
    }

    public void setRawText(String rawText) {
        this.rawText = rawText;
    }

    public String getRawImages() {
        return rawImages;
    }

    public void setRawImages(String rawImages) {
        this.rawImages = rawImages;
    }

    public LocalDateTime getScrapeTimestamp() {
        return scrapeTimestamp;
    }

    public void setScrapeTimestamp(LocalDateTime scrapeTimestamp) {
        this.scrapeTimestamp = scrapeTimestamp;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
