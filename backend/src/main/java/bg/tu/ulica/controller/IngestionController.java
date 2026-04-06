package bg.tu.ulica.controller;

import bg.tu.ulica.dto.IngestRequest;
import bg.tu.ulica.model.RawScrape;
import bg.tu.ulica.repository.RawScrapeRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/ingest")
public class IngestionController {

    private final RawScrapeRepository rawScrapeRepository;

    public IngestionController(RawScrapeRepository rawScrapeRepository) {
        this.rawScrapeRepository = rawScrapeRepository;
    }

    @PostMapping
    public ResponseEntity<RawScrape> ingestData(@RequestBody IngestRequest request) {
        if (request.getRawText() == null || request.getRawText().trim().isEmpty() || 
            request.getSourcePlatform() == null || request.getSourcePlatform().trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        RawScrape rawScrape = new RawScrape();
        rawScrape.setSourcePlatform(request.getSourcePlatform());
        rawScrape.setExternalId(request.getExternalId());
        rawScrape.setRawText(request.getRawText());
        rawScrape.setRawImages(request.getRawImages());
        // scrapeTimestamp and status are handled by default/creation timestamp

        RawScrape savedScrape = rawScrapeRepository.save(rawScrape);

        return ResponseEntity.ok(savedScrape);
    }
}
