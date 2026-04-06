package bg.tu.ulica.repository;

import bg.tu.ulica.model.RawScrape;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RawScrapeRepository extends JpaRepository<RawScrape, Long> {
}
