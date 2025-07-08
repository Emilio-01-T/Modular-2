"""
Factory module for modular-2 framework.
Handles dynamic creation of components from class paths.
"""
import logging
import importlib
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Factory:
    """
    Factory class for creating components dynamically from class paths.
    """
    
    def __init__(self):
        """Initialize the factory."""
        self.component_cache = {}
        logger.debug("🏭 Factory inizializzato")
    
    def create_component(self, component_type: str, class_path: str, config: Dict = None) -> Optional[Any]:
        """
        Create a component instance from class path.
        
        Args:
            component_type: Type of component (tool, agent, llm, etc.)
            class_path: Full class path (e.g., 'tools.math_tool.MathTool')
            config: Configuration dictionary for the component
            
        Returns:
            Component instance or None if creation failed
        """
        try:
            config = config or {}
            
            # Check cache first
            cache_key = f"{component_type}:{class_path}"
            if cache_key in self.component_cache:
                logger.debug(f"🔄 Componente '{class_path}' trovato in cache")
                # For tools and similar stateless components, we can reuse instances
                # For agents, we might want to create new instances
                if component_type in ["tool"]:
                    return self.component_cache[cache_key]
            
            # Parse class path
            module_path, class_name = self._parse_class_path(class_path)
            if not module_path or not class_name:
                logger.error(f"❌ Class path non valido: '{class_path}'")
                return None
            
            # Import module
            module = self._import_module(module_path)
            if not module:
                logger.error(f"❌ Impossibile importare modulo: '{module_path}'")
                return None
            
            # Get class
            component_class = self._get_class(module, class_name)
            if not component_class:
                logger.error(f"❌ Classe non trovata: '{class_name}' in '{module_path}'")
                return None
            
            # Create instance
            instance = self._create_instance(component_class, config)
            if instance:
                # Cache the instance for reuse
                self.component_cache[cache_key] = instance
                logger.info(f"✅ Componente '{class_path}' creato con successo")
                return instance
            else:
                logger.error(f"❌ Impossibile creare istanza di '{class_path}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore nella creazione componente '{class_path}': {e}")
            return None
    
    def _parse_class_path(self, class_path: str) -> tuple:
        """
        Parse class path into module path and class name.
        
        Args:
            class_path: Full class path
            
        Returns:
            Tuple of (module_path, class_name)
        """
        try:
            if '.' not in class_path:
                return None, None
            
            parts = class_path.split('.')
            class_name = parts[-1]
            module_path = '.'.join(parts[:-1])
            
            return module_path, class_name
            
        except Exception as e:
            logger.error(f"❌ Errore nel parsing class path '{class_path}': {e}")
            return None, None
    
    def _import_module(self, module_path: str) -> Optional[Any]:
        """
        Import module by path.
        
        Args:
            module_path: Module path to import
            
        Returns:
            Imported module or None
        """
        try:
            module = importlib.import_module(module_path)
            logger.debug(f"📦 Modulo '{module_path}' importato con successo")
            return module
            
        except ImportError as e:
            logger.error(f"❌ Errore nell'importazione modulo '{module_path}': {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Errore generico nell'importazione '{module_path}': {e}")
            return None
    
    def _get_class(self, module: Any, class_name: str) -> Optional[Any]:
        """
        Get class from module.
        
        Args:
            module: Imported module
            class_name: Name of the class to get
            
        Returns:
            Class object or None
        """
        try:
            if hasattr(module, class_name):
                component_class = getattr(module, class_name)
                logger.debug(f"🎯 Classe '{class_name}' trovata nel modulo")
                return component_class
            else:
                logger.error(f"❌ Classe '{class_name}' non trovata nel modulo")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore nel recupero classe '{class_name}': {e}")
            return None
    
    def _create_instance(self, component_class: Any, config: Dict) -> Optional[Any]:
        """
        Create instance of component class.
        
        Args:
            component_class: Class to instantiate
            config: Configuration for the instance
            
        Returns:
            Component instance or None
        """
        try:
            # Try different initialization patterns
            
            # Pattern 1: config parameter
            try:
                instance = component_class(config=config)
                logger.debug(f"✅ Istanza creata con pattern config")
                return instance
            except TypeError:
                pass
            
            # Pattern 2: no parameters
            try:
                instance = component_class()
                logger.debug(f"✅ Istanza creata senza parametri")
                return instance
            except TypeError:
                pass
            
            # Pattern 3: **config (unpack config as kwargs)
            try:
                instance = component_class(**config)
                logger.debug(f"✅ Istanza creata con **config")
                return instance
            except TypeError:
                pass
            
            # Pattern 4: positional arguments from config
            try:
                if config:
                    # Try to pass config values as positional args
                    args = list(config.values())
                    instance = component_class(*args)
                    logger.debug(f"✅ Istanza creata con args posizionali")
                    return instance
            except (TypeError, ValueError):
                pass
            
            logger.error(f"❌ Nessun pattern di inizializzazione funzionante per {component_class.__name__}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Errore nella creazione istanza: {e}")
            return None
    
    def clear_cache(self):
        """Clear the component cache."""
        self.component_cache.clear()
        logger.info("🧹 Cache componenti pulita")
    
    def get_cached_components(self) -> Dict[str, Any]:
        """Get all cached components."""
        return self.component_cache.copy()