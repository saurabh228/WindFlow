import React from 'react';
import './Carousel.css';
import CityCard from './CityCard';
import { 
  CarouselProvider, 
  Slider, 
  Slide, 
  ButtonBack, 
  ButtonNext 
} from 'pure-react-carousel';
import 'pure-react-carousel/dist/react-carousel.es.css';

const Carousel = ({ cities, currentWeather, rollUps, interval, handleSetInterval }) => {

  return (
 
      <CarouselProvider
        naturalSlideWidth={100}
        naturalSlideHeight={60}
        totalSlides={cities.length}
        visibleSlides={1}
      >
        <div className="carousel-container">
          <ButtonBack className="carousel-button left">‹</ButtonBack>
          <Slider>
            {cities.map((city, index) => (
              <Slide index={index} key={city}>
                <CityCard
                  city={city}
                  weather={currentWeather[city]}
                  rollUps={rollUps[city]}
                  interval={interval}
                  handleSetInterval={handleSetInterval}
                />
              </Slide>
            ))}
          </Slider>
          <ButtonNext className="carousel-button right">›</ButtonNext>
        </div>
      </CarouselProvider>
  );
};

export default Carousel;